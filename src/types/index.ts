// Order Types
export type OrderStatus = 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';

export interface OrderItem {
  id: string;
  name: string;
  quantity: number;
  price: number;
  description: string;
}

export interface Order {
  id: string;
  customerName: string;
  customerEmail: string;
  items: OrderItem[];
  total: number;
  status: OrderStatus;
  createdAt: string; // ISO string for DynamoDB
  updatedAt: string; // ISO string for DynamoDB
  estimatedDelivery?: string; // ISO string for DynamoDB
  trackingNumber?: string;
}

// Appointment Types
export interface Appointment {
  id: string;
  patientName: string;
  patientEmail: string;
  doctorName: string;
  date: string; // ISO string for DynamoDB
  duration: number; // in minutes
  type: 'consultation' | 'follow-up' | 'emergency' | 'routine';
  notes?: string;
  status: 'scheduled' | 'confirmed' | 'cancelled' | 'completed';
}

// DynamoDB Item Types
export interface OrderItemDynamo {
  id: string;
  customerName: string;
  customerEmail: string;
  items: OrderItem[];
  total: number;
  status: OrderStatus;
  createdAt: string;
  updatedAt: string;
  estimatedDelivery?: string;
  trackingNumber?: string;
  // Additional DynamoDB fields
  PK: string; // partition key: ORDER#{id}
  SK: string; // sort key: ORDER#{id}
  GSI1PK?: string; // customer email index
  GSI1SK?: string; // status + created date
}

export interface AppointmentItemDynamo {
  id: string;
  patientName: string;
  patientEmail: string;
  doctorName: string;
  date: string;
  duration: number;
  type: 'consultation' | 'follow-up' | 'emergency' | 'routine';
  notes?: string;
  status: 'scheduled' | 'confirmed' | 'cancelled' | 'completed';
  // Additional DynamoDB fields
  PK: string; // partition key: APPOINTMENT#{id}
  SK: string; // sort key: APPOINTMENT#{id}
  GSI1PK?: string; // patient email index
  GSI1SK?: string; // patient email
  GSI2PK?: string; // doctor name index
  GSI2SK?: string; // appointment date
  GSI3PK?: string; // status index
  GSI3SK?: string; // status
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

// Lambda Event Types
export interface APIGatewayEvent {
  httpMethod: string;
  path: string;
  pathParameters?: { [key: string]: string };
  queryStringParameters?: { [key: string]: string };
  headers?: { [key: string]: string };
  body?: string;
}

export interface APIGatewayResponse {
  statusCode: number;
  headers: { [key: string]: string };
  body: string;
} 