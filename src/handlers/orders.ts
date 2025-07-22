import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { getAllOrders, getOrderById as getOrderFromDB, createResponse } from '../utils/dynamodb';
import { ApiResponse } from '../types';

export const getOrders = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  try {
    console.log('getOrders called with event:', JSON.stringify(event, null, 2));

    const orders = await getAllOrders();
    
    const response: ApiResponse<typeof orders> = {
      success: true,
      data: orders,
      message: `Retrieved ${orders.length} orders successfully`
    };

    return createResponse(200, response);
  } catch (error) {
    console.error('Error in getOrders:', error);
    
    const errorResponse: ApiResponse<null> = {
      success: false,
      error: 'Internal server error',
      message: 'Failed to retrieve orders'
    };

    return createResponse(500, errorResponse);
  }
};

export const getOrderById = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  try {
    console.log('getOrderById called with event:', JSON.stringify(event, null, 2));

    const orderId = event.pathParameters?.id;
    
    if (!orderId) {
      const errorResponse: ApiResponse<null> = {
        success: false,
        error: 'Order ID is required',
        message: 'Please provide a valid order ID'
      };
      return createResponse(400, errorResponse);
    }

    // El campo id ya es numérico, así que podemos usarlo directamente
    const order = await getOrderFromDB(orderId);
    
    if (!order) {
      const errorResponse: ApiResponse<null> = {
        success: false,
        error: 'Order not found',
        message: `Order with ID ${orderId} was not found`
      };
      return createResponse(404, errorResponse);
    }

    const response: ApiResponse<typeof order> = {
      success: true,
      data: order,
      message: 'Order retrieved successfully'
    };

    return createResponse(200, response);
  } catch (error) {
    console.error('Error in getOrderById:', error);
    
    const errorResponse: ApiResponse<null> = {
      success: false,
      error: 'Internal server error',
      message: 'Failed to retrieve order'
    };

    return createResponse(500, errorResponse);
  }
}; 