import asyncio
import json
import base64
import warnings
import uuid
from s2s_events import S2sEvent
import time
from aws_sdk_bedrock_runtime.client import BedrockRuntimeClient, InvokeModelWithBidirectionalStreamOperationInput
from aws_sdk_bedrock_runtime.models import InvokeModelWithBidirectionalStreamInputChunk, BidirectionalInputPayloadPart
from aws_sdk_bedrock_runtime.config import Config, HTTPAuthSchemeResolver, SigV4AuthScheme
from smithy_aws_core.credentials_resolvers.environment import EnvironmentCredentialsResolver
from tool_processor import NovaSonicToolProcessor

# Suppress warnings
warnings.filterwarnings("ignore")

DEBUG = False

def debug_print(message):
    """Print only if debug mode is enabled"""
    if DEBUG:
        print(message)


class S2sSessionManager:
    """Manages bidirectional streaming with AWS Bedrock using asyncio"""
    
    def __init__(self, region, model_id='amazon.nova-sonic-v1:0'):
        """Initialize the stream manager."""
        self.model_id = model_id
        self.region = region
        
        # Audio and output queues
        self.audio_input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()
        
        self.response_task = None
        self.stream = None
        self.is_active = False
        self.bedrock_client = None
        
        # Session information
        self.prompt_name = None  # Will be set from frontend
        self.content_name = None  # Will be set from frontend
        self.audio_content_name = None  # Will be set from frontend
        self.toolUseContent = ""
        self.toolUseId = ""
        self.toolName = ""
        
        # Carlos's tool processor
        self.tool_processor = NovaSonicToolProcessor()

    def _initialize_client(self):
        """Initialize the Bedrock client."""
        config = Config(
            endpoint_uri=f"https://bedrock-runtime.{self.region}.amazonaws.com",
            region=self.region,
            aws_credentials_identity_resolver=EnvironmentCredentialsResolver(),
            http_auth_scheme_resolver=HTTPAuthSchemeResolver(),
            http_auth_schemes={"aws.auth#sigv4": SigV4AuthScheme()}
        )
        self.bedrock_client = BedrockRuntimeClient(config=config)

    async def initialize_stream(self):
        """Initialize the bidirectional stream with Bedrock."""
        try:
            if not self.bedrock_client:
                self._initialize_client()
        except Exception as ex:
            self.is_active = False
            print(f"Failed to initialize Bedrock client: {str(ex)}")
            raise

        try:
            # Initialize the stream
            self.stream = await self.bedrock_client.invoke_model_with_bidirectional_stream(
                InvokeModelWithBidirectionalStreamOperationInput(model_id=self.model_id)
            )
            self.is_active = True
            
            # Start listening for responses
            self.response_task = asyncio.create_task(self._process_responses())

            # Start processing audio input
            asyncio.create_task(self._process_audio_input())
            
            # Wait a bit to ensure everything is set up
            await asyncio.sleep(0.1)
            
            debug_print("Stream initialized successfully")
            return self
        except Exception as e:
            self.is_active = False
            print(f"Failed to initialize stream: {str(e)}")
            raise
    
    async def send_raw_event(self, event_data):
        try:
            """Send a raw event to the Bedrock stream."""
            if not self.stream or not self.is_active:
                debug_print("Stream not initialized or closed")
                return
            
            event_json = json.dumps(event_data)
            #if "audioInput" not in event_data["event"]:
            #    print(event_json)
            event = InvokeModelWithBidirectionalStreamInputChunk(
                value=BidirectionalInputPayloadPart(bytes_=event_json.encode('utf-8'))
            )
            await self.stream.input_stream.send(event)

            # Close session
            if "sessionEnd" in event_data["event"]:
                print("Session end detected, closing stream gracefully...")
                # Don't call close() here as it will be called by _process_responses
                # Just mark as inactive to stop processing
                self.is_active = False
            
        except Exception as e:
            debug_print(f"Error sending event: {str(e)}")
    
    async def _process_audio_input(self):
        """Process audio input from the queue and send to Bedrock."""
        consecutive_audio_errors = 0
        max_audio_errors = 5
        
        while self.is_active:
            try:
                # Get audio data from the queue with timeout
                try:
                    data = await asyncio.wait_for(self.audio_input_queue.get(), timeout=5.0)
                except asyncio.TimeoutError:
                    # No audio data for 5 seconds, check if still active
                    if not self.is_active:
                        break
                    continue
                
                # Extract data from the queue item
                prompt_name = data.get('prompt_name')
                content_name = data.get('content_name')
                audio_bytes = data.get('audio_bytes')
                
                if not audio_bytes or not prompt_name or not content_name:
                    debug_print("Missing required audio data properties")
                    continue

                # Create the audio input event
                audio_event = S2sEvent.audio_input(prompt_name, content_name, audio_bytes.decode('utf-8') if isinstance(audio_bytes, bytes) else audio_bytes)
                
                # Send the event
                await self.send_raw_event(audio_event)
                
                # Reset error counter on successful send
                consecutive_audio_errors = 0
                
            except asyncio.CancelledError:
                print("Audio processing task cancelled")
                break
            except Exception as e:
                consecutive_audio_errors += 1
                print(f"Error processing audio (attempt {consecutive_audio_errors}/{max_audio_errors}): {e}")
                
                if consecutive_audio_errors >= max_audio_errors:
                    print(f"Too many audio processing errors ({consecutive_audio_errors}), stopping audio processing")
                    break
                
                if DEBUG:
                    import traceback
                    traceback.print_exc()
        
        print("Audio processing loop ended")
    
    def add_audio_chunk(self, prompt_name, content_name, audio_data):
        """Add an audio chunk to the queue."""
        # The audio_data is already a base64 string from the frontend
        self.audio_input_queue.put_nowait({
            'prompt_name': prompt_name,
            'content_name': content_name,
            'audio_bytes': audio_data
        })
    
    async def _process_responses(self):
        """Process incoming responses from Bedrock."""
        consecutive_errors = 0
        max_consecutive_errors = 3
        retry_delay = 1.0  # Start with 1 second delay
        last_response_time = time.time()
        max_no_response_time = 30.0  # 30 seconds without response
        
        while self.is_active:
            try:
                # Check for stuck stream (no response for too long)
                current_time = time.time()
                if current_time - last_response_time > max_no_response_time:
                    print(f"No response from Bedrock for {max_no_response_time}s, stream may be stuck")
                    print("Breaking connection to allow reconnection")
                    break
                
                if not self.stream:
                    print("Stream is None, breaking")
                    break
                    
                output = await self.stream.await_output()
                result = await output[1].receive()
                
                # Reset error counter and retry delay on successful response
                consecutive_errors = 0
                retry_delay = 1.0  # Reset delay
                last_response_time = time.time()  # Update last response time
                
                if result.value and result.value.bytes_:
                    response_data = result.value.bytes_.decode('utf-8')
                    
                    json_data = json.loads(response_data)
                    json_data["timestamp"] = int(time.time() * 1000)  # Milliseconds since epoch
                    
                    event_name = None
                    if 'event' in json_data:
                        event_name = list(json_data["event"].keys())[0]
                        
                        # Handle tool use detection
                        if event_name == 'toolUse':
                            self.toolUseContent = json_data['event']['toolUse']
                            self.toolName = json_data['event']['toolUse']['toolName']
                            self.toolUseId = json_data['event']['toolUse']['toolUseId']
                            debug_print(f"Tool use detected: {self.toolName}, ID: {self.toolUseId}")

                        # Process tool use when content ends
                        elif event_name == 'contentEnd' and json_data['event'][event_name].get('type') == 'TOOL':
                            prompt_name = json_data['event']['contentEnd'].get("promptName")
                            debug_print("Processing tool use and sending result")
                            toolResult = await self.processToolUse(self.toolName, self.toolUseContent)
                                
                            # Send tool start event
                            toolContent = str(uuid.uuid4())
                            tool_start_event = S2sEvent.content_start_tool(prompt_name, toolContent, self.toolUseId)
                            await self.send_raw_event(tool_start_event)
                            
                            # Send tool result event
                            if isinstance(toolResult, dict):
                                content_json_string = json.dumps(toolResult)
                            else:
                                content_json_string = toolResult

                            tool_result_event = S2sEvent.text_input_tool(prompt_name, toolContent, content_json_string)
                            #print("Tool result", tool_result_event)
                            await self.send_raw_event(tool_result_event)

                            # Send tool content end event
                            tool_content_end_event = S2sEvent.content_end(prompt_name, toolContent)
                            await self.send_raw_event(tool_content_end_event)
                    
                    # Forward all events to the frontend (frontend handles display logic)
                    await self.output_queue.put(json_data)


            except json.JSONDecodeError as ex:
                print(f"JSON decode error: {ex}")
                continue
            except StopAsyncIteration as ex:
                # Stream has ended
                print(f"Stream ended: {ex}")
                break
            except Exception as e:
                # Handle specific AWS CRT errors and connection issues
                error_str = str(e)
                consecutive_errors += 1
                
                if any(keyword in error_str for keyword in ["CANCELLED", "AWS_ERROR_UNKNOWN", "InvalidStateError", "Future", "cancelled"]):
                    print(f"AWS CRT error (connection closed or cancelled): {e}")
                    # This is normal when ending session, don't treat as error
                    break
                elif "Checksum mismatch" in error_str:
                    print(f"Checksum mismatch error (data corruption): {e}")
                    if consecutive_errors >= max_consecutive_errors:
                        print(f"Too many consecutive errors ({consecutive_errors}), breaking connection")
                        break
                    print("This is usually a temporary network issue. Continuing...")
                    continue  # Try to continue instead of breaking
                elif "ValidationException" in error_str:
                    error_message = str(e)
                    print(f"Validation error: {error_message}")
                    break
                elif any(keyword in error_str.lower() for keyword in ["unexpected error during processing", "internal server error", "service unavailable", "throttling"]):
                    print(f"AWS Bedrock service error: {e}")
                    if consecutive_errors >= max_consecutive_errors:
                        print(f"Too many consecutive errors ({consecutive_errors}), breaking connection")
                        break
                    print(f"This is an AWS service error. Waiting {retry_delay}s before retrying...")
                    await asyncio.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 10.0)  # Exponential backoff, max 10s
                    continue  # Try to continue for AWS service errors
                elif "StopAsyncIteration" in error_str or "stream ended" in error_str.lower():
                    print(f"Stream ended normally: {e}")
                    break
                else:
                    print(f"Error receiving response: {e}")
                    if consecutive_errors >= max_consecutive_errors:
                        print(f"Too many consecutive errors ({consecutive_errors}), breaking connection")
                        break
                    print("This may cause Audio Input to continue without response. Continuing...")
                    continue  # Try to continue for other errors

        self.is_active = False
        print("Response processing loop ended")
        await self.close()

    async def processToolUse(self, toolName, toolUseContent):
        """Return the tool result using Carlos's tool processor"""
        #print(f"Tool Use Content: {toolUseContent}")

        try:
            # Extract the tool content
            tool_content = toolUseContent.get("content", {})
            
            # Use Carlos's tool processor
            result = await self.tool_processor.process_tool_async(toolName, tool_content)
            
            if not result:
                result = "no result found"

            return {"result": result}
        except Exception as ex:
            print(f"Error in processToolUse: {ex}")
            return {"result": "An error occurred while attempting to retrieve information related to the toolUse event."}
    
    async def close(self):
        """Close the stream properly."""
        if not self.is_active:
            return
            
        self.is_active = False
        
        # Cancel all pending tasks
        if self.response_task and not self.response_task.done():
            self.response_task.cancel()
            try:
                await self.response_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Error waiting for response task: {e}")
        
        # Close stream if it exists
        if self.stream:
            try:
                await self.stream.input_stream.close()
            except Exception as e:
                print(f"Error closing stream: {e}")
        
        # Clear queues safely
        try:
            while not self.audio_input_queue.empty():
                try:
                    self.audio_input_queue.get_nowait()
                except:
                    pass
        except Exception as e:
            print(f"Error clearing audio queue: {e}")
            
        try:
            while not self.output_queue.empty():
                try:
                    self.output_queue.get_nowait()
                except:
                    pass
        except Exception as e:
            print(f"Error clearing output queue: {e}")
        
        # Reset state
        self.stream = None
        self.bedrock_client = None
        self.toolUseContent = ""
        self.toolUseId = ""
        self.toolName = "" 