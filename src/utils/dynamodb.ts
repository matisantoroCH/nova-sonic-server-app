import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, ScanCommand, GetCommand, QueryCommand } from '@aws-sdk/lib-dynamodb';
import { OrderItemDynamo, AppointmentItemDynamo, Order, Appointment } from '../types';

// Initialize DynamoDB client
const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);

// Table names from environment variables
const ORDERS_TABLE = process.env.ORDERS_TABLE!;
const APPOINTMENTS_TABLE = process.env.APPOINTMENTS_TABLE!;

// Helper function to create API Gateway response
export const createResponse = (statusCode: number, body: any, headers: Record<string, string> = {}) => {
  return {
    statusCode,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
      'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
      ...headers
    },
    body: JSON.stringify(body)
  };
};

// Helper function to convert DynamoDB item to Order
export const convertDynamoOrderToOrder = (item: OrderItemDynamo): Order => {
  return {
    id: item.id,
    customerName: item.customerName,
    customerEmail: item.customerEmail,
    items: item.items,
    total: item.total,
    status: item.status,
    createdAt: item.createdAt,
    updatedAt: item.updatedAt,
    estimatedDelivery: item.estimatedDelivery,
    trackingNumber: item.trackingNumber
  };
};

// Helper function to convert DynamoDB item to Appointment
export const convertDynamoAppointmentToAppointment = (item: AppointmentItemDynamo): Appointment => {
  return {
    id: item.id,
    patientName: item.patientName,
    patientEmail: item.patientEmail,
    doctorName: item.doctorName,
    date: item.date,
    duration: item.duration,
    type: item.type,
    notes: item.notes,
    status: item.status
  };
};

// Orders Database Operations
export const getAllOrders = async (): Promise<Order[]> => {
  try {
    const command = new ScanCommand({
      TableName: ORDERS_TABLE,
      FilterExpression: 'begins_with(PK, :pk)',
      ExpressionAttributeValues: {
        ':pk': 'ORDER#'
      }
    });

    const response = await docClient.send(command);
    
    if (!response.Items) {
      return [];
    }

    return response.Items
      .map(item => convertDynamoOrderToOrder(item as OrderItemDynamo))
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  } catch (error) {
    console.error('Error getting all orders:', error);
    throw error;
  }
};

export const getOrderById = async (orderId: string): Promise<Order | null> => {
  try {
    const command = new GetCommand({
      TableName: ORDERS_TABLE,
      Key: {
        PK: `ORDER#${orderId}`,
        SK: `ORDER#${orderId}`
      }
    });

    const response = await docClient.send(command);
    
    if (!response.Item) {
      return null;
    }

    return convertDynamoOrderToOrder(response.Item as OrderItemDynamo);
  } catch (error) {
    console.error('Error getting order by ID:', error);
    throw error;
  }
};

export const getOrdersByCustomerEmail = async (customerEmail: string): Promise<Order[]> => {
  try {
    const command = new QueryCommand({
      TableName: ORDERS_TABLE,
      IndexName: 'CustomerEmailIndex',
      KeyConditionExpression: 'customerEmail = :email',
      ExpressionAttributeValues: {
        ':email': customerEmail
      }
    });

    const response = await docClient.send(command);
    
    if (!response.Items) {
      return [];
    }

    return response.Items
      .map(item => convertDynamoOrderToOrder(item as OrderItemDynamo))
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  } catch (error) {
    console.error('Error getting orders by customer email:', error);
    throw error;
  }
};

export const getOrdersByStatus = async (status: string): Promise<Order[]> => {
  try {
    const command = new QueryCommand({
      TableName: ORDERS_TABLE,
      IndexName: 'StatusIndex',
      KeyConditionExpression: '#status = :status',
      ExpressionAttributeNames: {
        '#status': 'status'
      },
      ExpressionAttributeValues: {
        ':status': status
      }
    });

    const response = await docClient.send(command);
    
    if (!response.Items) {
      return [];
    }

    return response.Items
      .map(item => convertDynamoOrderToOrder(item as OrderItemDynamo))
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  } catch (error) {
    console.error('Error getting orders by status:', error);
    throw error;
  }
};

// Appointments Database Operations
export const getAllAppointments = async (): Promise<Appointment[]> => {
  try {
    const command = new ScanCommand({
      TableName: APPOINTMENTS_TABLE,
      FilterExpression: 'begins_with(PK, :pk)',
      ExpressionAttributeValues: {
        ':pk': 'APPOINTMENT#'
      }
    });

    const response = await docClient.send(command);
    
    if (!response.Items) {
      return [];
    }

    return response.Items
      .map(item => convertDynamoAppointmentToAppointment(item as AppointmentItemDynamo))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  } catch (error) {
    console.error('Error getting all appointments:', error);
    throw error;
  }
};

export const getAppointmentById = async (appointmentId: string): Promise<Appointment | null> => {
  try {
    const command = new GetCommand({
      TableName: APPOINTMENTS_TABLE,
      Key: {
        PK: `APPOINTMENT#${appointmentId}`,
        SK: `APPOINTMENT#${appointmentId}`
      }
    });

    const response = await docClient.send(command);
    
    if (!response.Item) {
      return null;
    }

    return convertDynamoAppointmentToAppointment(response.Item as AppointmentItemDynamo);
  } catch (error) {
    console.error('Error getting appointment by ID:', error);
    throw error;
  }
};

export const getAppointmentsByDate = async (date: string): Promise<Appointment[]> => {
  try {
    // Convert date to YYYY-MM-DD format for comparison
    const targetDate = new Date(date).toISOString().split('T')[0];
    
    const command = new ScanCommand({
      TableName: APPOINTMENTS_TABLE,
      FilterExpression: 'begins_with(#date, :date)',
      ExpressionAttributeNames: {
        '#date': 'date'
      },
      ExpressionAttributeValues: {
        ':date': targetDate
      }
    });

    const response = await docClient.send(command);
    
    if (!response.Items) {
      return [];
    }

    return response.Items
      .map(item => convertDynamoAppointmentToAppointment(item as AppointmentItemDynamo))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  } catch (error) {
    console.error('Error getting appointments by date:', error);
    throw error;
  }
};

export const getAppointmentsByPatientEmail = async (patientEmail: string): Promise<Appointment[]> => {
  try {
    const command = new QueryCommand({
      TableName: APPOINTMENTS_TABLE,
      IndexName: 'PatientEmailIndex',
      KeyConditionExpression: 'patientEmail = :email',
      ExpressionAttributeValues: {
        ':email': patientEmail
      }
    });

    const response = await docClient.send(command);
    
    if (!response.Items) {
      return [];
    }

    return response.Items
      .map(item => convertDynamoAppointmentToAppointment(item as AppointmentItemDynamo))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  } catch (error) {
    console.error('Error getting appointments by patient email:', error);
    throw error;
  }
};

export const getAppointmentsByDoctorAndDate = async (doctorName: string, date: string): Promise<Appointment[]> => {
  try {
    const targetDate = new Date(date).toISOString().split('T')[0];
    
    const command = new QueryCommand({
      TableName: APPOINTMENTS_TABLE,
      IndexName: 'DoctorDateIndex',
      KeyConditionExpression: 'doctorName = :doctor AND begins_with(appointmentDate, :date)',
      ExpressionAttributeValues: {
        ':doctor': doctorName,
        ':date': targetDate
      }
    });

    const response = await docClient.send(command);
    
    if (!response.Items) {
      return [];
    }

    return response.Items
      .map(item => convertDynamoAppointmentToAppointment(item as AppointmentItemDynamo))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  } catch (error) {
    console.error('Error getting appointments by doctor and date:', error);
    throw error;
  }
}; 