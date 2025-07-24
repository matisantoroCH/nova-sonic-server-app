import json

class S2sEvent:
  # Default configuration values
  DEFAULT_INFER_CONFIG = {
        "maxTokens": 1024,
        "topP": 0.95,
        "temperature": 0.7
    }
  
  # Carlos's system prompt
  DEFAULT_SYSTEM_PROMPT = "Eres Carlos, el asistente virtual de Nova Sonic. " \
    "Eres amable, profesional y hablas en español argentino. " \
    "Tu función es ayudar a los usuarios con: " \
    "- Consultar, cancelar y crear pedidos " \
    "- Agendar, cancelar, modificar y consultar citas médicas " \
    "Siempre responde de forma clara y natural. " \
    "Si necesitas más información, pídela amablemente. " \
    "IMPORTANTE: Cuando uses herramientas (tools), SIEMPRE envía los números como dígitos, no como palabras. " \
    "Por ejemplo: usa '6' en lugar de 'seis', '627' en lugar de 'seiscientos veintisiete', '10065' en lugar de 'diez mil sesenta y cinco'. " \
    "Esto es crucial para que las herramientas funcionen correctamente."

  DEFAULT_AUDIO_INPUT_CONFIG = {
        "mediaType":"audio/lpcm",
        "sampleRateHertz":16000,
        "sampleSizeBits":16,
        "channelCount":1,
        "audioType":"SPEECH","encoding":"base64"
      }
  DEFAULT_AUDIO_OUTPUT_CONFIG = {
          "mediaType": "audio/lpcm",
          "sampleRateHertz": 24000,
          "sampleSizeBits": 16,
          "channelCount": 1,
          "voiceId": "carlos",
          "encoding": "base64",
          "audioType": "SPEECH"
        }
  
  # Carlos's custom tools configuration
  DEFAULT_TOOL_CONFIG = {
          "tools": [
              {
                  "toolSpec": {
                      "name": "consultarOrder",
                      "description": "Consultar el estado y detalles de un pedido por ID",
                      "inputSchema": {
                          "json": '''{
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "type": "object",
                            "properties": {
                                "orderId": {
                                    "type": "string",
                                    "description": "ID del pedido a consultar"
                                }
                            },
                            "required": ["orderId"]
                        }'''
                      }
                  }
              },
              {
                  "toolSpec": {
                      "name": "cancelarOrder",
                      "description": "Cancelar un pedido existente por ID",
                      "inputSchema": {
                          "json": '''{
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "type": "object",
                            "properties": {
                                "orderId": {
                                    "type": "string",
                                    "description": "ID del pedido a cancelar"
                                }
                            },
                            "required": ["orderId"]
                        }'''
                      }
                  }
              },
              {
                  "toolSpec": {
                      "name": "crearOrder",
                      "description": "Crear un nuevo pedido con items y datos del cliente",
                      "inputSchema": {
                          "json": '''{
                            "$schema": "http://json-schema.org/draft-07/schema#",
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
                        }'''
                      }
                  }
              },
              {
                  "toolSpec": {
                      "name": "agendarTurno",
                      "description": "Agendar una nueva cita médica",
                      "inputSchema": {
                          "json": '''{
                            "$schema": "http://json-schema.org/draft-07/schema#",
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
                        }'''
                      }
                  }
              },
              {
                  "toolSpec": {
                      "name": "cancelarTurno",
                      "description": "Cancelar una cita médica existente",
                      "inputSchema": {
                          "json": '''{
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "type": "object",
                            "properties": {
                                "appointmentId": {
                                    "type": "string",
                                    "description": "ID de la cita a cancelar"
                                }
                            },
                            "required": ["appointmentId"]
                        }'''
                      }
                  }
              },
              {
                  "toolSpec": {
                      "name": "modificarTurno",
                      "description": "Modificar la fecha u hora de una cita médica",
                      "inputSchema": {
                          "json": '''{
                            "$schema": "http://json-schema.org/draft-07/schema#",
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
                        }'''
                      }
                  }
              },
              {
                  "toolSpec": {
                      "name": "consultarTurno",
                      "description": "Consultar los detalles de una cita médica",
                      "inputSchema": {
                          "json": '''{
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "type": "object",
                            "properties": {
                                "appointmentId": {
                                    "type": "string",
                                    "description": "ID de la cita a consultar"
                                }
                            },
                            "required": ["appointmentId"]
                        }'''
                      }
                  }
              }
          ]
        }

  @staticmethod
  def session_start(inference_config=DEFAULT_INFER_CONFIG): 
    return {"event":{"sessionStart":{"inferenceConfiguration":inference_config}}}

  @staticmethod
  def prompt_start(prompt_name, 
                   audio_output_config=DEFAULT_AUDIO_OUTPUT_CONFIG, 
                   tool_config=DEFAULT_TOOL_CONFIG):
    return {
          "event": {
            "promptStart": {
              "promptName": prompt_name,
              "textOutputConfiguration": {
                "mediaType": "text/plain"
              },
              "audioOutputConfiguration": audio_output_config,
              "toolUseOutputConfiguration": {
                "mediaType": "application/json"
              },
              "toolConfiguration": tool_config
            }
          }
        }

  @staticmethod
  def content_start_text(prompt_name, content_name):
    return {
        "event":{
        "contentStart":{
          "promptName":prompt_name,
          "contentName":content_name,
          "type":"TEXT",
          "interactive":True,
          "role": "SYSTEM",
          "textInputConfiguration":{
            "mediaType":"text/plain"
            }
          }
        }
      }
    
  @staticmethod
  def text_input(prompt_name, content_name, system_prompt=DEFAULT_SYSTEM_PROMPT):
    return {
      "event":{
        "textInput":{
          "promptName":prompt_name,
          "contentName":content_name,
          "content":system_prompt,
        }
      }
    }
  
  @staticmethod
  def content_end(prompt_name, content_name):
    return {
      "event":{
        "contentEnd":{
          "promptName":prompt_name,
          "contentName":content_name
        }
      }
    }

  @staticmethod
  def content_start_audio(prompt_name, content_name, audio_input_config=DEFAULT_AUDIO_INPUT_CONFIG):
    return {
      "event":{
        "contentStart":{
          "promptName":prompt_name,
          "contentName":content_name,
          "type":"AUDIO",
          "interactive":True,
          "audioInputConfiguration":audio_input_config
        }
      }
    }
    
  @staticmethod
  def audio_input(prompt_name, content_name, content):
    return {
      "event": {
        "audioInput": {
          "promptName": prompt_name,
          "contentName": content_name,
          "content": content,
        }
      }
    }
  
  @staticmethod
  def content_start_tool(prompt_name, content_name, tool_use_id):
    return {
        "event": {
          "contentStart": {
            "promptName": prompt_name,
            "contentName": content_name,
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
      }
  
  @staticmethod
  def text_input_tool(prompt_name, content_name, content):
    return {
      "event": {
        "toolResult": {
          "promptName": prompt_name,
          "contentName": content_name,
          "content": content,
          #"role": "TOOL"
        }
      }
    }
  
  @staticmethod
  def prompt_end(prompt_name):
    return {
      "event": {
        "promptEnd": {
          "promptName": prompt_name
        }
      }
    }
  
  @staticmethod
  def session_end():
    return  {
      "event": {
        "sessionEnd": {}
      }
    } 