import asyncio
import websockets
import json
import logging
import warnings
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'nova_sonic'))
from nova_sonic.nova_sonic_client import NovaSonicClient
import argparse
import http.server
import threading
from http import HTTPStatus

# Configure logging
LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings("ignore")

DEBUG = False

def debug_print(message):
    """Print only if debug mode is enabled"""
    if DEBUG:
        print(message)


class HealthCheckHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        client_ip = self.client_address[0]
        logger.info(
            f"Health check request received from {client_ip} for path: {self.path}"
        )

        if self.path == "/health" or self.path == "/":
            logger.info(f"Responding with 200 OK to health check from {client_ip}")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = json.dumps({"status": "healthy"})
            self.wfile.write(response.encode("utf-8"))
            logger.info(f"Health check response sent: {response}")
        else:
            logger.info(
                f"Responding with 404 Not Found to request for {self.path} from {client_ip}"
            )
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()

    def log_message(self, format, *args):
        # Override to use our logger instead
        pass


def start_health_check_server(health_host, health_port):
    """Start the HTTP health check server on port 80."""
    try:
        # Create the server with a socket timeout to prevent hanging
        httpd = http.server.HTTPServer((health_host, health_port), HealthCheckHandler)
        httpd.timeout = 5  # 5 second timeout

        logger.info(f"Starting health check server on {health_host}:{health_port}")

        # Run the server in a separate thread
        thread = threading.Thread(target=httpd.serve_forever)
        thread.daemon = (
            True  # This ensures the thread will exit when the main program exits
        )
        thread.start()

        # Verify the server is running
        logger.info(
            f"Health check server started at http://{health_host}:{health_port}/health"
        )
        logger.info(f"Health check thread is alive: {thread.is_alive()}")

        # Try to make a local request to verify the server is responding
        try:
            import urllib.request

            with urllib.request.urlopen(
                f"http://localhost:{health_port}/health", timeout=2
            ) as response:
                logger.info(
                    f"Local health check test: {response.status} - {response.read().decode('utf-8')}"
                )
        except Exception as e:
            logger.warning(f"Local health check test failed: {e}")

    except Exception as e:
        logger.error(f"Failed to start health check server: {e}", exc_info=True)


async def websocket_handler(websocket):
    """Handle WebSocket connections from the frontend."""
    nova_client = None
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                message_type = data.get('type')
                
                print(f"📨 Mensaje recibido: {message_type}")
                
                if message_type == 'start_session':
                    # Initialize Nova Sonic client
                    nova_client = NovaSonicClient()
                    await nova_client.initialize_stream()
                    
                    # Set WebSocket callback for transcriptions
                    async def send_transcription_to_frontend(message):
                        try:
                            await websocket.send(json.dumps(message))
                        except Exception as e:
                            print(f"Error sending transcription: {e}")
                    
                    nova_client.websocket_callback = send_transcription_to_frontend
                    
                    # Start audio processing tasks
                    audio_tasks = [
                        asyncio.create_task(audio_output_handler(websocket, nova_client))
                    ]
                    
                    await websocket.send(json.dumps({
                        'type': 'session_started',
                        'payload': {
                            'sessionId': 'session-' + str(id(websocket)),
                            'message': 'Sesión de Nova Sonic iniciada',
                            'promptName': nova_client.prompt_name,
                            'systemContentName': nova_client.system_content_name,
                            'audioContentName': nova_client.audio_content_name
                        }
                    }))
                    
                    print("✅ Sesión iniciada")
                    
                elif message_type == 's2s_event':
                    if not nova_client:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'payload': {'message': 'Sesión no activa'}
                        }))
                        continue
                    
                    # Send S2S event directly to Bedrock (like in the workshop)
                    event_data = data.get('payload', {})
                    print(f"📤 Enviando evento S2S a Bedrock: {json.dumps(event_data)[:200]}...")
                    
                    # Check if this is an audio input event
                    if 'event' in event_data and 'audioInput' in event_data['event']:
                        # Handle audio input specially
                        audio_content = event_data['event']['audioInput']['content']
                        await nova_client.process_audio_from_frontend(audio_content)
                    else:
                        # Send other events directly
                        await nova_client._send_event(json.dumps(event_data))
                    
                elif message_type == 'end_session':
                    if nova_client:
                        await nova_client.stop_session()
                        nova_client = None
                    
                    await websocket.send(json.dumps({
                        'type': 'session_ended',
                        'payload': {
                            'message': 'Sesión finalizada'
                        }
                    }))
                    
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'payload': {'message': 'Mensaje JSON inválido'}
                }))
            except Exception as e:
                print(f"❌ Error procesando mensaje: {str(e)}")
                await websocket.send(json.dumps({
                    'type': 'error',
                    'payload': {'message': f'Error: {str(e)}'}
                }))
                
    except websockets.exceptions.ConnectionClosed:
        print("🔌 WebSocket connection closed")
    finally:
        if nova_client:
            await nova_client.stop_session()


async def audio_output_handler(websocket, nova_client):
    """Handle audio output from Nova Sonic"""
    try:
        while True:
            try:
                # Get audio from Nova Sonic's output queue
                audio_data = await asyncio.wait_for(
                    nova_client.audio_output_queue.get(),
                    timeout=0.1
                )
                
                # Encode audio data as base64 for frontend
                import base64
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                # Send audio to frontend
                await websocket.send(json.dumps({
                    'type': 'audio_response',
                    'payload': {
                        'audioData': audio_base64
                    }
                }))
                
            except asyncio.TimeoutError:
                # No audio data available, continue
                continue
            except Exception as e:
                print(f"❌ Error en audio_output_handler: {str(e)}")
                break
                
    except Exception as e:
        print(f"❌ Error en audio_output_handler: {str(e)}")


async def main(host, port, health_port):
    """Main function to start the WebSocket server"""
    print(f"🚀 Iniciando servidor WebSocket en {host}:{port}")
    
    # Start health check server
    start_health_check_server(host, health_port)
    
    # Start WebSocket server
    async with websockets.serve(websocket_handler, host, port):
        print(f"✅ Servidor WebSocket iniciado en ws://{host}:{port}")
        print(f"✅ Servidor de health check en http://{host}:{health_port}/health")
        print("🔄 Esperando conexiones...")
        
        # Keep the server running
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nova Sonic WebSocket Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="WebSocket port")
    parser.add_argument("--health-port", type=int, default=80, help="Health check port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    if args.debug:
        DEBUG = True
        print("🔧 Debug mode enabled")
    
    try:
        asyncio.run(main(args.host, args.port, args.health_port))
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {str(e)}")
        sys.exit(1) 