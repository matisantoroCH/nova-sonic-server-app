import { APIGatewayEvent, APIGatewayProxyResult } from 'aws-lambda';
import { getOrders, getOrderById } from './orders';
import { getAppointments, getAppointmentById } from './appointments';

export const handler = async (event: APIGatewayEvent): Promise<APIGatewayProxyResult> => {
  try {
    const { path, httpMethod } = event;
    
    // Extract the path without query parameters
    const cleanPath = path?.split('?')[0] || '';
    
    // Route based on HTTP method and path
    switch (`${httpMethod} ${cleanPath}`) {
      case 'GET /orders':
        return await getOrders(event);
        
      case 'GET /orders/{id}':
        return await getOrderById(event);
        
      case 'GET /appointments':
        return await getAppointments(event);
        
      case 'GET /appointments/{id}':
        return await getAppointmentById(event);
        
      default:
        return {
          statusCode: 404,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET'
          },
          body: JSON.stringify({
            message: 'Endpoint not found',
            path: cleanPath,
            method: httpMethod
          })
        };
    }
  } catch (error) {
    console.error('Error in API handler:', error);
    
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET'
      },
      body: JSON.stringify({
        message: 'Internal server error',
        error: process.env.NODE_ENV === 'development' ? (error as Error).message : 'Something went wrong'
      })
    };
  }
}; 