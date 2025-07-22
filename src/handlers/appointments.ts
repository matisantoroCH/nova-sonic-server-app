import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { getAllAppointments, getAppointmentById as getAppointmentFromDB, getAppointmentsByDate, createResponse } from '../utils/dynamodb';
import { ApiResponse } from '../types';

export const getAppointments = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  try {
    console.log('getAppointments called with event:', JSON.stringify(event, null, 2));

    // Check if date parameter is provided
    const date = event.queryStringParameters?.date;
    
    let appointments;
    if (date) {
      appointments = await getAppointmentsByDate(date);
    } else {
      appointments = await getAllAppointments();
    }
    
    const response: ApiResponse<typeof appointments> = {
      success: true,
      data: appointments,
      message: `Retrieved ${appointments.length} appointments successfully`
    };

    return createResponse(200, response);
  } catch (error) {
    console.error('Error in getAppointments:', error);
    
    const errorResponse: ApiResponse<null> = {
      success: false,
      error: 'Internal server error',
      message: 'Failed to retrieve appointments'
    };

    return createResponse(500, errorResponse);
  }
};

export const getAppointmentById = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  try {
    console.log('getAppointmentById called with event:', JSON.stringify(event, null, 2));

    const appointmentId = event.pathParameters?.id;
    
    if (!appointmentId) {
      const errorResponse: ApiResponse<null> = {
        success: false,
        error: 'Appointment ID is required',
        message: 'Please provide a valid appointment ID'
      };
      return createResponse(400, errorResponse);
    }

    // El campo id ya es numérico, así que podemos usarlo directamente
    const appointment = await getAppointmentFromDB(appointmentId);
    
    if (!appointment) {
      const errorResponse: ApiResponse<null> = {
        success: false,
        error: 'Appointment not found',
        message: `Appointment with ID ${appointmentId} was not found`
      };
      return createResponse(404, errorResponse);
    }

    const response: ApiResponse<typeof appointment> = {
      success: true,
      data: appointment,
      message: 'Appointment retrieved successfully'
    };

    return createResponse(200, response);
  } catch (error) {
    console.error('Error in getAppointmentById:', error);
    
    const errorResponse: ApiResponse<null> = {
      success: false,
      error: 'Internal server error',
      message: 'Failed to retrieve appointment'
    };

    return createResponse(500, errorResponse);
  }
}; 