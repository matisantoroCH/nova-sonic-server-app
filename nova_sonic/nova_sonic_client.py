import os
import asyncio
import base64
import json
import uuid
import pyaudio
import boto3
from aws_sdk_bedrock_runtime.client import BedrockRuntimeClient, InvokeModelWithBidirectionalStreamOperationInput
from aws_sdk_bedrock_runtime.models import InvokeModelWithBidirectionalStreamInputChunk, BidirectionalInputPayloadPart
from aws_sdk_bedrock_runtime.config import Config, HTTPAuthSchemeResolver, SigV4AuthScheme
from smithy_aws_core.credentials_resolvers.environment import EnvironmentCredentialsResolver
from tool_processor import NovaSonicToolProcessor

# Audio configuration
INPUT_SAMPLE_RATE = 16000
OUTPUT_SAMPLE_RATE = 24000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK_SIZE = 1024

class NovaSonicClient:
    """Nova Sonic client for voice interaction with orders and appointments"""
    
    def __init__(self, voice_id="carlos", language_code="es-ES", region="us-east-1"):
        self.voice_id = voice_id
        self.language_code = language_code
        self.model_id = "amazon.nova-sonic-v1:0"
        self.region = region
        self.bedrock_client = None
        self.stream = None
        self.is_active = False
        self.tool_processor = NovaSonicToolProcessor()
        
        # Session information
        self.prompt_name = str(uuid.uuid4())
        self.system_content_name = str(uuid.uuid4())
        self.audio_content_name = str(uuid.uuid4())
        
        # Audio components
        self.p = None
        self.input_stream = None
        self.output_stream = None
        self.audio_input_queue = asyncio.Queue()
        self.audio_output_queue = asyncio.Queue()
        
        # Tool tracking
        self.pending_tool_tasks = {}
        
        # Conversation tracking (like in the working example)
        self.conversation_history = []
        self.last_user_text = None
        self.last_assistant_text = None
        self._printed_hashes = set()

    def _initialize_client(self):
        """Initialize the Bedrock client with boto3 credential chain"""
        # Use environment credentials resolver
        credentials_resolver = EnvironmentCredentialsResolver()

        config = Config(
            endpoint_uri=f"https://bedrock-runtime.{self.region}.amazonaws.com",
            region=self.region,
            aws_credentials_identity_resolver=credentials_resolver,
            http_auth_scheme_resolver=HTTPAuthSchemeResolver(),
            http_auth_schemes={"aws.auth#sigv4": SigV4AuthScheme()}
        )
        self.bedrock_client = BedrockRuntimeClient(config=config)

    async def initialize_stream(self):
        """Initialize the bidirectional stream with Bedrock"""
        if not self.bedrock_client:
            self._initialize_client()
        
        try:
            self.stream = await self.bedrock_client.invoke_model_with_bidirectional_stream(
                InvokeModelWithBidirectionalStreamOperationInput(model_id=self.model_id)
            )
            self.is_active = True
            
            # Send initialization events in the correct order (following nova_sonic.py)
            await self._send_event(self._session_start_event())
            await self._send_event(self._prompt_start_event())
            await self._send_event(self._content_start_event())
            await self._send_event(self._system_prompt_event())
            await self._send_event(self._content_end_event())
            await self._send_event(self._audio_content_start_event())
            
            # Start processing responses
            asyncio.create_task(self._process_responses())
            
            print("✅ Nova Sonic stream inicializado correctamente")
            return self
            
        except Exception as e:
            self.is_active = False
            print(f"❌ Error inicializando stream: {str(e)}")
            raise

    async def _send_event(self, event_json):
        """Send an event to the Bedrock stream"""
        if not self.stream or not self.is_active:
            return
        
        event = InvokeModelWithBidirectionalStreamInputChunk(
            value=BidirectionalInputPayloadPart(bytes_=event_json.encode('utf-8'))
        )
        
        try:
            await self.stream.input_stream.send(event)
        except Exception as e:
            print(f"Error enviando evento: {str(e)}")

    def _session_start_event(self):
        """Create session start event"""
        return json.dumps({
            "event": {
                "sessionStart": {
                    "inferenceConfiguration": {
                        "maxTokens": 1024,
                        "topP": 0.9,
                        "temperature": 0.7
                    }
                }
            }
        })

    def _prompt_start_event(self):
        """Create prompt start event with tool definitions"""
        # Tool schemas
        consultar_order_schema = {
            "type": "object",
            "properties": {
                "orderId": {
                    "type": "string",
                    "description": "ID del pedido a consultar"
                }
            },
            "required": ["orderId"]
        }
        
        cancelar_order_schema = {
            "type": "object",
            "properties": {
                "orderId": {
                    "type": "string",
                    "description": "ID del pedido a cancelar"
                }
            },
            "required": ["orderId"]
        }
        
        crear_order_schema = {
            "type": "object",
            "properties": {
                "customerName": {
                    "type": "string",
                    "description": "Nombre completo del cliente"
                },
                "customerEmail": {
                    "type": "string",
                    "description": "Email del cliente"
                },
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "quantity": {"type": "integer"},
                            "price": {"type": "number"},
                            "description": {"type": "string"}
                        }
                    },
                    "description": "Lista de productos en el pedido"
                }
            },
            "required": ["customerName", "customerEmail", "items"]
        }
        
        agendar_turno_schema = {
            "type": "object",
            "properties": {
                "patientName": {
                    "type": "string",
                    "description": "Nombre completo del paciente"
                },
                "patientEmail": {
                    "type": "string",
                    "description": "Email del paciente"
                },
                "doctorName": {
                    "type": "string",
                    "description": "Nombre del doctor"
                },
                "date": {
                    "type": "string",
                    "description": "Fecha y hora de la cita (ISO format)"
                },
                "duration": {
                    "type": "integer",
                    "description": "Duración en minutos"
                },
                "type": {
                    "type": "string",
                    "description": "Tipo de cita (consultation, follow-up, emergency, routine)"
                },
                "notes": {
                    "type": "string",
                    "description": "Notas adicionales"
                }
            },
            "required": ["patientName", "patientEmail", "doctorName", "date"]
        }
        
        cancelar_turno_schema = {
            "type": "object",
            "properties": {
                "appointmentId": {
                    "type": "string",
                    "description": "ID de la cita a cancelar"
                }
            },
            "required": ["appointmentId"]
        }
        
        modificar_turno_schema = {
            "type": "object",
            "properties": {
                "appointmentId": {
                    "type": "string",
                    "description": "ID de la cita a modificar"
                },
                "newDate": {
                    "type": "string",
                    "description": "Nueva fecha (opcional)"
                },
                "newTime": {
                    "type": "string",
                    "description": "Nueva hora (opcional)"
                }
            },
            "required": ["appointmentId"]
        }
        
        consultar_turno_schema = {
            "type": "object",
            "properties": {
                "appointmentId": {
                    "type": "string",
                    "description": "ID de la cita a consultar"
                }
            },
            "required": ["appointmentId"]
        }
        
        return json.dumps({
            "event": {
                "promptStart": {
                    "promptName": self.prompt_name,
                    "textOutputConfiguration": {
                        "mediaType": "text/plain"
                    },
                    "audioOutputConfiguration": {
                        "mediaType": "audio/lpcm",
                        "sampleRateHertz": OUTPUT_SAMPLE_RATE,
                        "sampleSizeBits": 16,
                        "channelCount": 1,
                        "voiceId": self.voice_id,
                        "encoding": "base64",
                        "audioType": "SPEECH"
                    },
                    "toolUseOutputConfiguration": {
                        "mediaType": "application/json"
                    },
                    "toolConfiguration": {
                        "tools": [
                            {
                                "toolSpec": {
                                    "name": "consultarOrder",
                                    "description": "Consultar el estado y detalles de un pedido por ID",
                                    "inputSchema": {"json": json.dumps(consultar_order_schema)}
                                }
                            },
                            {
                                "toolSpec": {
                                    "name": "cancelarOrder",
                                    "description": "Cancelar un pedido existente por ID",
                                    "inputSchema": {"json": json.dumps(cancelar_order_schema)}
                                }
                            },
                            {
                                "toolSpec": {
                                    "name": "crearOrder",
                                    "description": "Crear un nuevo pedido con items y datos del cliente",
                                    "inputSchema": {"json": json.dumps(crear_order_schema)}
                                }
                            },
                            {
                                "toolSpec": {
                                    "name": "agendarTurno",
                                    "description": "Agendar una nueva cita médica",
                                    "inputSchema": {"json": json.dumps(agendar_turno_schema)}
                                }
                            },
                            {
                                "toolSpec": {
                                    "name": "cancelarTurno",
                                    "description": "Cancelar una cita médica existente",
                                    "inputSchema": {"json": json.dumps(cancelar_turno_schema)}
                                }
                            },
                            {
                                "toolSpec": {
                                    "name": "modificarTurno",
                                    "description": "Modificar la fecha u hora de una cita médica",
                                    "inputSchema": {"json": json.dumps(modificar_turno_schema)}
                                }
                            },
                            {
                                "toolSpec": {
                                    "name": "consultarTurno",
                                    "description": "Consultar los detalles de una cita médica",
                                    "inputSchema": {"json": json.dumps(consultar_turno_schema)}
                                }
                            }
                        ]
                    }
                }
            }
        })

    def _content_start_event(self):
        """Create content start event for system prompt"""
        return json.dumps({
            "event": {
                "contentStart": {
                    "promptName": self.prompt_name,
                    "contentName": self.system_content_name,
                    "type": "TEXT",
                    "interactive": True,
                    "role": "SYSTEM",
                    "textInputConfiguration": {
                        "mediaType": "text/plain"
                    }
                }
            }
        })

    def _system_prompt_event(self):
        """Create system prompt event"""
        system_prompt = (
            "Eres Carlos, el asistente virtual de Nova Sonic. "
            "Eres amable, profesional y hablas en español argentino. "
            "Tu función es ayudar a los usuarios con: "
            "- Consultar, cancelar y crear pedidos "
            "- Agendar, cancelar, modificar y consultar citas médicas "
            "Siempre responde de forma clara y natural. "
            "Si necesitas más información, pídela amablemente. "
            "IMPORTANTE: Cuando uses herramientas (tools), SIEMPRE envía los números como dígitos, no como palabras. "
            "Por ejemplo: usa '6' en lugar de 'seis', '627' en lugar de 'seiscientos veintisiete', '10065' en lugar de 'diez mil sesenta y cinco'. "
            "Esto es crucial para que las herramientas funcionen correctamente."
        )
        return json.dumps({
            "event": {
                "textInput": {
                    "promptName": self.prompt_name,
                    "contentName": self.system_content_name,
                    "content": system_prompt
                }
            }
        })

    def _content_end_event(self):
        """Create content end event"""
        return json.dumps({
            "event": {
                "contentEnd": {
                    "promptName": self.prompt_name,
                    "contentName": self.system_content_name
                }
            }
        })

    def _audio_content_start_event(self):
        """Create audio content start event"""
        return json.dumps({
            "event": {
                "contentStart": {
                    "promptName": self.prompt_name,
                    "contentName": self.audio_content_name,
                    "type": "AUDIO",
                    "interactive": True,
                    "role": "USER",
                    "audioInputConfiguration": {
                        "mediaType": "audio/lpcm",
                        "sampleRateHertz": INPUT_SAMPLE_RATE,
                        "sampleSizeBits": 16,
                        "channelCount": 1,
                        "audioType": "SPEECH",
                        "encoding": "base64"
                    }
                }
            }
        })

    def _audio_content_end_event(self):
        """Create audio content end event"""
        return json.dumps({
            "event": {
                "contentEnd": {
                    "promptName": self.prompt_name,
                    "contentName": self.audio_content_name
                }
            }
        })

    def _prompt_end_event(self):
        """Create prompt end event"""
        return json.dumps({
            "event": {
                "promptEnd": {
                    "promptName": self.prompt_name
                }
            }
        })

    def _session_end_event(self):
        """Create session end event"""
        return json.dumps({
            "event": {
                "sessionEnd": {}
            }
        })

    async def _send_audio_chunk(self, audio_bytes: bytes):
        """Send audio chunk to the stream"""
        blob = base64.b64encode(audio_bytes)
        audio_event = json.dumps({
            "event": {
                "audioInput": {
                    "promptName": self.prompt_name,
                    "contentName": self.audio_content_name,
                    "content": blob.decode('utf-8')
                }
            }
        })
        await self._send_event(audio_event)

    async def _process_responses(self):
        """Process responses from the stream"""
        try:
            if not self.stream:
                print("❌ No hay stream de respuesta disponible")
                return
                
            while self.is_active:
                try:
                    output = await self.stream.await_output()
                    result = await output[1].receive()
                    if result.value and result.value.bytes_:
                        response_data = result.value.bytes_.decode('utf-8')
                        json_data = json.loads(response_data)
                        if 'event' in json_data:
                            if 'toolUse' in json_data['event']:
                                tool_use = json_data['event']['toolUse']
                                tool_name = tool_use['toolName']
                                tool_use_id = tool_use['toolUseId']
                                asyncio.create_task(self._handle_tool(tool_name, tool_use, tool_use_id))
                            if 'textOutput' in json_data['event']:
                                text = json_data['event']['textOutput']['content']
                                role = json_data['event']['textOutput']['role']
                                if text.strip() == '{ "interrupted" : true }' or '{ "interrupted" : true }' in text:
                                    continue
                                text_hash = hash((role, text.strip()))
                                if text_hash in self._printed_hashes:
                                    continue
                                self._printed_hashes.add(text_hash)
                                if role == "ASSISTANT":
                                    self.last_assistant_text = text
                                    self.conversation_history.append({"role": "assistant", "content": text})
                                    print(f"[{role}] {text}")
                                elif role == "USER":
                                    self.last_user_text = text
                                    self.conversation_history.append({"role": "user", "content": text})
                                    print(f"[{role}] {text}")
                            if 'audioOutput' in json_data['event']:
                                audio_content = json_data['event']['audioOutput']['content']
                                audio_bytes = base64.b64decode(audio_content)
                                await self.audio_output_queue.put(audio_bytes)
                                
                except StopAsyncIteration:
                    # Stream has ended
                    break
                except Exception as e:
                    print(f"Error receiving response: {e}")
                    break
                    
        except Exception as e:
            print(f"Error procesando respuestas: {str(e)}")
        finally:
            self.is_active = False

    async def _handle_tool(self, tool_name, tool_use, tool_use_id):
        """Handle tool execution"""
        try:
            # 1. contentStart (TOOL)
            await self._send_event(json.dumps({
                "event": {
                    "contentStart": {
                        "promptName": self.prompt_name,
                        "contentName": tool_use_id,
                        "interactive": False,
                        "type": "TOOL",
                        "role": "TOOL",
                        "toolResultInputConfiguration": {
                            "toolUseId": tool_use_id,
                            "type": "TEXT",
                            "textInputConfiguration": {
                                "mediaType": "text/plain"
                            }
                        }
                    }
                }
            }))
            
            # 2. toolResult (content como objeto JSON, NO string)
            # Extraer el contenido específico de la herramienta
            tool_content = tool_use.get('content', {})
            print(f"🔧 Debug - Tool: {tool_name}, Content: {tool_content}")
            result = await self.tool_processor.process_tool_async(tool_name, tool_content)
            await self._send_event(json.dumps({
                "event": {
                    "toolResult": {
                        "promptName": self.prompt_name,
                        "contentName": tool_use_id,
                        "content": json.dumps(result, default=str)
                    }
                }
            }))
            
            # 3. contentEnd (TOOL)
            await self._send_event(json.dumps({
                "event": {
                    "contentEnd": {
                        "promptName": self.prompt_name,
                        "contentName": tool_use_id,
                        "type": "TOOL"
                    }
                }
            }))
            
            print(f"✅ Herramienta {tool_name} ejecutada: {result}")
            
        except Exception as e:
            print(f"Error manejando herramienta {tool_name}: {str(e)}")

    def add_audio_chunk(self, audio_bytes: bytes):
        """Add audio chunk to the input queue"""
        if self.is_active:
            try:
                # Use a thread-safe way to add to queue
                loop = asyncio.get_event_loop()
                if loop and loop.is_running():
                    loop.call_soon_threadsafe(self.audio_input_queue.put_nowait, {'audio_bytes': audio_bytes})
                else:
                    # Fallback: just put directly if no loop available
                    self.audio_input_queue.put_nowait({'audio_bytes': audio_bytes})
            except RuntimeError:
                # No event loop in current thread, use a different approach
                try:
                    self.audio_input_queue.put_nowait({'audio_bytes': audio_bytes})
                except Exception as e:
                    pass  # Silently ignore if queue is full
            except Exception as e:
                pass  # Silently ignore other errors

    async def capture_audio(self):
        """Capture audio from microphone"""
        try:
            # Initialize PyAudio
            self.p = pyaudio.PyAudio()
            
            # Open input stream
            self.input_stream = self.p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=INPUT_SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE
            )
            
            # Open output stream
            self.output_stream = self.p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=OUTPUT_SAMPLE_RATE,
                output=True,
                frames_per_buffer=CHUNK_SIZE
            )
            
            print("🎤 Sesión de audio iniciada. Habla ahora...")
            
            while self.is_active:
                audio_data = self.input_stream.read(CHUNK_SIZE, exception_on_overflow=False)
                await self._send_audio_chunk(audio_data)
                await asyncio.sleep(0.01)  # Add delay like in the example
                
        except Exception as e:
            print(f"Error capturing audio: {e}")
        finally:
            if self.input_stream:
                self.input_stream.stop_stream()
                self.input_stream.close()
            if self.output_stream:
                self.output_stream.stop_stream()
                self.output_stream.close()
            if self.p:
                self.p.terminate()
            await self._send_event(self._audio_content_end_event())

    async def play_output_audio(self):
        """Play output audio from queue"""
        try:
            while self.is_active:
                audio_data = await self.audio_output_queue.get()
                if audio_data and self.output_stream:
                    self.output_stream.write(audio_data)
        except Exception as e:
            print(f"Error playing audio: {e}")

    async def stop_session(self):
        """Stop the Nova Sonic session"""
        if not self.is_active:
            return
        
        self.is_active = False
        
        # Cancel pending tool tasks
        for task in self.pending_tool_tasks.values():
            task.cancel()
        
        # Send end events
        await self._send_event(self._prompt_end_event())
        await self._send_event(self._session_end_event())
        
        # Close stream
        if self.stream:
            await self.stream.input_stream.close()
        
        print("🛑 Sesión de Nova Sonic finalizada") 