import os
import asyncio
import json
import boto3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from decimal import Decimal
import uuid
import pytz

def convert_decimals(obj):
    """Convert Decimal objects to float/int for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj) if obj % 1 != 0 else int(obj)
    elif isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    else:
        return obj

class NovaSonicToolProcessor:
    """Tool processor for Nova Sonic integration with orders and appointments"""
    
    def __init__(self):
        # Use boto3's default credential provider chain
        # This will automatically try: environment variables, AWS CLI profile, IAM roles, etc.
        self.dynamodb = boto3.resource('dynamodb')
        self.orders_table = self.dynamodb.Table(os.getenv('ORDERS_TABLE', 'nova-sonic-server-app-demo-orders'))
        self.appointments_table = self.dynamodb.Table(os.getenv('APPOINTMENTS_TABLE', 'nova-sonic-server-app-demo-appointments'))

    def _get_argentina_time(self) -> str:
        """Get current time in Argentina timezone (UTC-3)"""
        argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')
        now = datetime.now(argentina_tz)
        return now.isoformat()

    async def _get_next_order_id(self) -> int:
        """Obtiene el siguiente número de pedido"""
        try:
            # Buscar el último número usado
            response = self.orders_table.scan(
                ProjectionExpression='id'
            )
            
            numbers = [int(item.get('id', 0)) for item in response.get('Items', []) if item.get('id', '').isdigit()]
            return max(numbers) + 1 if numbers else 1
        except Exception:
            return 1

    async def _get_next_appointment_id(self) -> int:
        """Obtiene el siguiente número de cita"""
        try:
            # Buscar el último número usado
            response = self.appointments_table.scan(
                ProjectionExpression='id'
            )
            
            numbers = [int(item.get('id', 0)) for item in response.get('Items', []) if item.get('id', '').isdigit()]
            return max(numbers) + 1 if numbers else 1
        except Exception:
            return 1

    async def process_tool_async(self, tool_name: str, tool_content: Dict[str, Any]) -> Dict[str, Any]:
        """Process a tool request asynchronously"""
        tool = tool_name.lower()
        
        # Parse tool_content if it's a JSON string
        if isinstance(tool_content, str):
            try:
                tool_content = json.loads(tool_content)
            except json.JSONDecodeError:
                return {"error": f"Contenido de herramienta inválido: {tool_content}"}
        
        if tool == "consultarorder":
            return await self._consultar_pedido(tool_content)
        elif tool == "cancelarorder":
            return await self._cancelar_pedido(tool_content)
        elif tool == "crearorder":
            return await self._crear_pedido(tool_content)
        elif tool == "agendarturno":
            return await self._agendar_turno(tool_content)
        elif tool == "cancelarturno":
            return await self._cancelar_turno(tool_content)
        elif tool == "modificarturno":
            return await self._modificar_turno(tool_content)
        elif tool == "consultarturno":
            return await self._consultar_turno(tool_content)
        else:
            return {"error": f"Herramienta no soportada: {tool_name}"}

    async def _consultar_pedido(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar un pedido por ID"""
        try:
            # Handle both orderId and order_id formats
            order_id = content.get("orderId") or content.get("order_id")
            if not order_id:
                return {"error": "Se requiere el ID del pedido"}
            
            # Buscar directamente por PK/SK usando el ID
            response = self.orders_table.get_item(Key={"PK": f"ORDER#{order_id}", "SK": f"ORDER#{order_id}"})
            item = response.get("Item")
            
            if not item:
                return {"error": f"Pedido {order_id} no encontrado"}
            
            return {
                "success": True,
                "order": convert_decimals({
                    "id": item.get("id"),
                    "customerName": item.get("customerName"),
                    "customerEmail": item.get("customerEmail"),
                    "total": item.get("total"),
                    "status": item.get("status"),
                    "createdAt": item.get("createdAt"),
                    "estimatedDelivery": item.get("estimatedDelivery"),
                    "trackingNumber": item.get("trackingNumber"),
                    "items": item.get("items", [])
                })
            }
        except Exception as e:
            return {"error": f"Error consultando pedido: {str(e)}"}

    async def _cancelar_pedido(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Cancelar un pedido"""
        try:
            # Handle both orderId and order_id formats
            order_id = content.get("orderId") or content.get("order_id")
            if not order_id:
                return {"error": "Se requiere el ID del pedido"}

            # Buscar el pedido
            response = self.orders_table.get_item(Key={"PK": f"ORDER#{order_id}", "SK": f"ORDER#{order_id}"})
            item = response.get("Item")
            
            if not item:
                return {"error": f"Pedido {order_id} no encontrado"}
            
            if item.get("status") == "cancelled":
                return {"error": "El pedido ya está cancelado"}
            
            # Actualizar estado
            self.orders_table.update_item(
                Key={"PK": f"ORDER#{order_id}", "SK": f"ORDER#{order_id}"},
                UpdateExpression="SET #status = :status, updatedAt = :updatedAt",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":status": "cancelled",
                    ":updatedAt": self._get_argentina_time()
                }
            )
            
            return {
                "success": True,
                "message": f"Pedido #{order_id} cancelado exitosamente",
                "orderId": order_id
            }
        except Exception as e:
            return {"error": f"Error cancelando pedido: {str(e)}"}

    async def _crear_pedido(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Crear un nuevo pedido"""
        try:
            customer_name = content.get("customerName")
            customer_email = content.get("customerEmail")
            items = content.get("items", [])
            
            if not customer_name or not customer_email:
                return {"error": "Se requiere nombre y email del cliente"}
            
            if not items:
                return {"error": "Se requiere al menos un item en el pedido"}
            
            # Calcular total - convertir a Decimal para DynamoDB
            total = sum(Decimal(str(item.get("price", 0))) * Decimal(str(item.get("quantity", 1))) for item in items)
            
            # Crear pedido con ID numérico
            order_id = str(await self._get_next_order_id())
            now = self._get_argentina_time()
            # Calcular fecha de entrega estimada (5 días desde ahora en zona horaria de Argentina)
            argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')
            estimated_delivery = (datetime.now(argentina_tz) + timedelta(days=5)).isoformat()
            
            # Convertir items a Decimal para DynamoDB
            processed_items = []
            for item in items:
                processed_item = item.copy()
                processed_item["price"] = Decimal(str(item.get("price", 0)))
                processed_item["quantity"] = Decimal(str(item.get("quantity", 1)))
                processed_items.append(processed_item)
            
            order_item = {
                "id": order_id,
                "customerName": customer_name,
                "customerEmail": customer_email,
                "items": processed_items,
                "total": total,
                "status": "pending",
                "createdAt": now,
                "updatedAt": now,
                "estimatedDelivery": estimated_delivery,
                "PK": f"ORDER#{order_id}",
                "SK": f"ORDER#{order_id}",
                "GSI1PK": customer_email,
                "GSI1SK": f"pending#{now}"
            }
            
            self.orders_table.put_item(Item=order_item)
            
            return {
                "success": True,
                "message": f"Pedido #{order_id} creado exitosamente",
                "orderId": order_id,
                "total": total,
                "estimatedDelivery": estimated_delivery
            }
        except Exception as e:
            return {"error": f"Error creando pedido: {str(e)}"}

    async def _agendar_turno(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Agendar un nuevo turno/cita"""
        try:
            patient_name = content.get("patientName")
            patient_email = content.get("patientEmail")
            doctor_name = content.get("doctorName")
            date = content.get("date")
            duration = content.get("duration", 30)
            type_appointment = content.get("type", "consultation")
            notes = content.get("notes", "")
            
            if not all([patient_name, patient_email, doctor_name, date]):
                return {"error": "Se requiere nombre del paciente, email, doctor y fecha"}
            
            # Crear cita con ID numérico
            appointment_id = str(await self._get_next_appointment_id())
            now = self._get_argentina_time()
            
            appointment_item = {
                "id": appointment_id,
                "patientName": patient_name,
                "patientEmail": patient_email,
                "doctorName": doctor_name,
                "date": date,
                "duration": duration,
                "type": type_appointment,
                "notes": notes,
                "status": "scheduled",
                "PK": f"APPOINTMENT#{appointment_id}",
                "SK": f"APPOINTMENT#{appointment_id}",
                "GSI1PK": patient_email,
                "GSI1SK": patient_email,
                "GSI2PK": doctor_name,
                "GSI2SK": date,
                "GSI3PK": "scheduled",
                "GSI3SK": "scheduled"
            }
            
            self.appointments_table.put_item(Item=appointment_item)
            
            return {
                "success": True,
                "message": f"Cita #{appointment_id} agendada exitosamente",
                "appointmentId": appointment_id,
                "date": date,
                "doctorName": doctor_name
            }
        except Exception as e:
            return {"error": f"Error agendando cita: {str(e)}"}

    async def _cancelar_turno(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Cancelar un turno/cita"""
        try:
            # Handle both appointmentId and appointment_id formats
            appointment_id = content.get("appointmentId") or content.get("appointment_id")
            if not appointment_id:
                return {"error": "Se requiere el ID de la cita"}
            
            # Buscar la cita
            response = self.appointments_table.get_item(Key={"PK": f"APPOINTMENT#{appointment_id}", "SK": f"APPOINTMENT#{appointment_id}"})
            item = response.get("Item")
            
            if not item:
                return {"error": f"Cita {appointment_id} no encontrada"}
            
            if item.get("status") == "cancelled":
                return {"error": "La cita ya está cancelada"}
            
            # Actualizar estado
            self.appointments_table.update_item(
                Key={"PK": f"APPOINTMENT#{appointment_id}", "SK": f"APPOINTMENT#{appointment_id}"},
                UpdateExpression="SET #status = :status",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={":status": "cancelled"}
            )
            
            return {
                "success": True,
                "message": f"Cita #{appointment_id} cancelada exitosamente",
                "appointmentId": appointment_id
            }
        except Exception as e:
            return {"error": f"Error cancelando cita: {str(e)}"}

    async def _modificar_turno(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Modificar fecha u hora de un turno"""
        try:
            appointment_id = content.get("appointmentId")
            new_date = content.get("newDate")
            new_time = content.get("newTime")
            
            if not appointment_id:
                return {"error": "Se requiere el ID de la cita"}
            
            if not new_date and not new_time:
                return {"error": "Se requiere nueva fecha o nueva hora"}
            
            # Buscar la cita
            response = self.appointments_table.get_item(Key={"PK": f"APPOINTMENT#{appointment_id}", "SK": f"APPOINTMENT#{appointment_id}"})
            item = response.get("Item")
            
            if not item:
                return {"error": f"Cita {appointment_id} no encontrada"}
            
            # Construir nueva fecha/hora
            current_date = datetime.fromisoformat(item.get("date").replace("Z", "+00:00"))
            
            if new_date:
                # Si se proporciona nueva fecha, mantener la hora actual
                new_date_obj = datetime.fromisoformat(new_date.replace("Z", "+00:00"))
                new_datetime = current_date.replace(year=new_date_obj.year, month=new_date_obj.month, day=new_date_obj.day)
            elif new_time:
                # Si se proporciona nueva hora, mantener la fecha actual
                new_time_obj = datetime.fromisoformat(new_time.replace("Z", "+00:00"))
                new_datetime = current_date.replace(hour=new_time_obj.hour, minute=new_time_obj.minute)
            else:
                new_datetime = current_date
            
            # Actualizar cita
            update_expression = "SET #date = :date"
            expression_values = {":date": new_datetime.isoformat() + "Z"}
            
            self.appointments_table.update_item(
                Key={"PK": f"APPOINTMENT#{appointment_id}", "SK": f"APPOINTMENT#{appointment_id}"},
                UpdateExpression=update_expression,
                ExpressionAttributeNames={"#date": "date"},
                ExpressionAttributeValues=expression_values
            )
            
            return {
                "success": True,
                "message": f"Cita #{appointment_id} modificada exitosamente",
                "appointmentId": appointment_id,
                "newDate": new_datetime.isoformat() + "Z"
            }
        except Exception as e:
            return {"error": f"Error modificando cita: {str(e)}"}

    async def _consultar_turno(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar un turno/cita"""
        try:
            # Handle both appointmentId and appointment_id formats
            appointment_id = content.get("appointmentId") or content.get("appointment_id")
            if not appointment_id:
                return {"error": "Se requiere el ID de la cita"}
            
            # Buscar la cita
            response = self.appointments_table.get_item(Key={"PK": f"APPOINTMENT#{appointment_id}", "SK": f"APPOINTMENT#{appointment_id}"})
            item = response.get("Item")
            
            if not item:
                return {"error": f"Cita {appointment_id} no encontrada"}
            
            return {
                "success": True,
                "appointment": convert_decimals({
                    "id": item.get("id"),
                    "patientName": item.get("patientName"),
                    "patientEmail": item.get("patientEmail"),
                    "doctorName": item.get("doctorName"),
                    "date": item.get("date"),
                    "status": item.get("status"),
                    "type": item.get("type"),
                    "duration": item.get("duration"),
                    "notes": item.get("notes")
                })
            }
        except Exception as e:
            return {"error": f"Error consultando cita: {str(e)}"} 