const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, PutCommand } = require('@aws-sdk/lib-dynamodb');

// Initialize DynamoDB client
const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);

// Table names from environment variables
const ORDERS_TABLE = process.env.ORDERS_TABLE || 'nova-sonic-server-app-demo-orders';
const APPOINTMENTS_TABLE = process.env.APPOINTMENTS_TABLE || 'nova-sonic-server-app-demo-appointments';

const sampleOrders = [
  {
    id: '1',
    customerName: 'María González',
    customerEmail: 'maria.gonzalez@email.com',
    items: [
      { id: '1', name: 'Laptop Dell Inspiron 15', quantity: 1, price: 899.99, description: 'Laptop de 15 pulgadas, Intel i5, 8GB RAM, 256GB SSD' },
      { id: '2', name: 'Mouse inalámbrico Logitech', quantity: 2, price: 29.99, description: 'Mouse óptico inalámbrico con receptor USB' }
    ],
    total: 959.97,
    status: 'pending',
    createdAt: '2025-07-15T10:30:00.000Z',
    updatedAt: '2025-07-15T10:30:00.000Z',
    estimatedDelivery: '2025-07-20T00:00:00.000Z',
    PK: 'ORDER#1',
    SK: 'ORDER#1',
    GSI1PK: 'maria.gonzalez@email.com',
    GSI1SK: 'pending#2025-07-15T10:30:00.000Z'
  },
  {
    id: '2',
    customerName: 'Carlos Mendoza',
    customerEmail: 'carlos.mendoza@email.com',
    items: [
      { id: '3', name: 'Monitor Samsung 24"', quantity: 1, price: 199.99, description: 'Monitor LED Full HD 1920x1080, 60Hz' },
      { id: '4', name: 'Teclado mecánico RGB', quantity: 1, price: 89.99, description: 'Teclado mecánico con switches Cherry MX Blue' }
    ],
    total: 289.98,
    status: 'processing',
    createdAt: '2025-07-14T14:15:00.000Z',
    updatedAt: '2025-07-16T09:45:00.000Z',
    trackingNumber: 'TRK789456123',
    PK: 'ORDER#2',
    SK: 'ORDER#2',
    GSI1PK: 'carlos.mendoza@email.com',
    GSI1SK: 'processing#2025-07-14T14:15:00.000Z'
  },
  {
    id: '3',
    customerName: 'Ana Rodríguez',
    customerEmail: 'ana.rodriguez@email.com',
    items: [
      { id: '5', name: 'iPhone 15 Pro', quantity: 1, price: 1199.99, description: 'iPhone 15 Pro 128GB, Titanio Natural' },
      { id: '6', name: 'Carcasa protectora', quantity: 1, price: 39.99, description: 'Carcasa de silicona transparente para iPhone 15 Pro' }
    ],
    total: 1239.98,
    status: 'shipped',
    createdAt: '2025-07-13T11:20:00.000Z',
    updatedAt: '2025-07-17T16:30:00.000Z',
    trackingNumber: 'TRK456789321',
    estimatedDelivery: '2025-07-19T00:00:00.000Z',
    PK: 'ORDER#3',
    SK: 'ORDER#3',
    GSI1PK: 'ana.rodriguez@email.com',
    GSI1SK: 'shipped#2025-07-13T11:20:00.000Z'
  },
  {
    id: '4',
    customerName: 'Luis Fernández',
    customerEmail: 'luis.fernandez@email.com',
    items: [
      { id: '7', name: 'Auriculares Sony WH-1000XM5', quantity: 1, price: 349.99, description: 'Auriculares inalámbricos con cancelación de ruido' },
      { id: '8', name: 'Cable USB-C', quantity: 3, price: 12.99, description: 'Cable USB-C de alta velocidad 100W' }
    ],
    total: 388.96,
    status: 'delivered',
    createdAt: '2025-07-10T08:45:00.000Z',
    updatedAt: '2025-07-12T14:20:00.000Z',
    trackingNumber: 'TRK123789456',
    PK: 'ORDER#4',
    SK: 'ORDER#4',
    GSI1PK: 'luis.fernandez@email.com',
    GSI1SK: 'delivered#2025-07-10T08:45:00.000Z'
  },
  {
    id: '5',
    customerName: 'Carmen Silva',
    customerEmail: 'carmen.silva@email.com',
    items: [
      { id: '9', name: 'Tablet Samsung Galaxy Tab S9', quantity: 1, price: 649.99, description: 'Tablet Android 11 pulgadas, 128GB' },
      { id: '10', name: 'Funda con teclado', quantity: 1, price: 79.99, description: 'Funda protectora con teclado bluetooth' }
    ],
    total: 729.98,
    status: 'cancelled',
    createdAt: '2025-07-08T16:30:00.000Z',
    updatedAt: '2025-07-09T10:15:00.000Z',
    PK: 'ORDER#5',
    SK: 'ORDER#5',
    GSI1PK: 'carmen.silva@email.com',
    GSI1SK: 'cancelled#2025-07-08T16:30:00.000Z'
  },
  {
    id: '6',
    customerName: 'Roberto Vargas',
    customerEmail: 'roberto.vargas@email.com',
    items: [
      { id: '11', name: 'Smartwatch Apple Watch Series 9', quantity: 1, price: 399.99, description: 'Apple Watch Series 9 GPS 41mm' },
      { id: '12', name: 'Banda deportiva', quantity: 2, price: 49.99, description: 'Banda de silicona deportiva para Apple Watch' }
    ],
    total: 499.97,
    status: 'pending',
    createdAt: '2025-07-18T12:00:00.000Z',
    updatedAt: '2025-07-18T12:00:00.000Z',
    estimatedDelivery: '2025-07-23T00:00:00.000Z',
    PK: 'ORDER#6',
    SK: 'ORDER#6',
    GSI1PK: 'roberto.vargas@email.com',
    GSI1SK: 'pending#2025-07-18T12:00:00.000Z'
  },
  {
    id: '7',
    customerName: 'Elena Martínez',
    customerEmail: 'elena.martinez@email.com',
    items: [
      { id: '13', name: 'Cámara Canon EOS R7', quantity: 1, price: 1499.99, description: 'Cámara mirrorless APS-C, 33MP, 4K video' },
      { id: '14', name: 'Lente 24-70mm f/2.8', quantity: 1, price: 899.99, description: 'Lente zoom profesional RF 24-70mm' }
    ],
    total: 2399.98,
    status: 'processing',
    createdAt: '2025-07-17T09:30:00.000Z',
    updatedAt: '2025-07-19T15:45:00.000Z',
    trackingNumber: 'TRK987321654',
    PK: 'ORDER#7',
    SK: 'ORDER#7',
    GSI1PK: 'elena.martinez@email.com',
    GSI1SK: 'processing#2025-07-17T09:30:00.000Z'
  }
];

// Sample Appointments Data - Updated with recent dates from July 2025 onwards
const sampleAppointments = [
  {
    id: '1',
    patientName: 'María González',
    patientEmail: 'maria.gonzalez@email.com',
    doctorName: 'Dr. Carlos Rodríguez',
    date: '2025-07-22T10:00:00.000Z',
    duration: 30,
    type: 'consultation',
    notes: 'Consulta de rutina - Control anual',
    status: 'scheduled',
    PK: 'APPOINTMENT#1',
    SK: 'APPOINTMENT#1',
    GSI1PK: 'maria.gonzalez@email.com',
    GSI1SK: 'maria.gonzalez@email.com',
    GSI2PK: 'Dr. Carlos Rodríguez',
    GSI2SK: '2025-07-22T10:00:00.000Z',
    GSI3PK: 'scheduled',
    GSI3SK: 'scheduled'
  },
  {
    id: '2',
    patientName: 'Luis Fernández',
    patientEmail: 'luis.fernandez@email.com',
    doctorName: 'Dra. Ana López',
    date: '2025-07-24T14:30:00.000Z',
    duration: 45,
    type: 'follow-up',
    notes: 'Seguimiento post-cirugía de rodilla',
    status: 'confirmed',
    PK: 'APPOINTMENT#2',
    SK: 'APPOINTMENT#2',
    GSI1PK: 'luis.fernandez@email.com',
    GSI1SK: 'luis.fernandez@email.com',
    GSI2PK: 'Dra. Ana López',
    GSI2SK: '2025-07-24T14:30:00.000Z',
    GSI3PK: 'confirmed',
    GSI3SK: 'confirmed'
  },
  {
    id: '3',
    patientName: 'Carmen Silva',
    patientEmail: 'carmen.silva@email.com',
    doctorName: 'Dr. Roberto Mendoza',
    date: '2025-07-25T09:00:00.000Z',
    duration: 60,
    type: 'emergency',
    notes: 'Dolor agudo en el pecho - Requiere evaluación inmediata',
    status: 'scheduled',
    PK: 'APPOINTMENT#3',
    SK: 'APPOINTMENT#3',
    GSI1PK: 'carmen.silva@email.com',
    GSI1SK: 'carmen.silva@email.com',
    GSI2PK: 'Dr. Roberto Mendoza',
    GSI2SK: '2025-07-25T09:00:00.000Z',
    GSI3PK: 'scheduled',
    GSI3SK: 'scheduled'
  },
  {
    id: '4',
    patientName: 'Carlos Mendoza',
    patientEmail: 'carlos.mendoza@email.com',
    doctorName: 'Dr. Carlos Rodríguez',
    date: '2025-07-22T11:00:00.000Z',
    duration: 30,
    type: 'routine',
    notes: 'Control de presión arterial y diabetes',
    status: 'confirmed',
    PK: 'APPOINTMENT#4',
    SK: 'APPOINTMENT#4',
    GSI1PK: 'carlos.mendoza@email.com',
    GSI1SK: 'carlos.mendoza@email.com',
    GSI2PK: 'Dr. Carlos Rodríguez',
    GSI2SK: '2025-07-22T11:00:00.000Z',
    GSI3PK: 'confirmed',
    GSI3SK: 'confirmed'
  },
  {
    id: '5',
    patientName: 'Elena Martínez',
    patientEmail: 'elena.martinez@email.com',
    doctorName: 'Dra. Ana López',
    date: '2025-07-26T16:00:00.000Z',
    duration: 45,
    type: 'consultation',
    notes: 'Primera consulta - Evaluación general',
    status: 'scheduled',
    PK: 'APPOINTMENT#5',
    SK: 'APPOINTMENT#5',
    GSI1PK: 'elena.martinez@email.com',
    GSI1SK: 'elena.martinez@email.com',
    GSI2PK: 'Dra. Ana López',
    GSI2SK: '2025-07-26T16:00:00.000Z',
    GSI3PK: 'scheduled',
    GSI3SK: 'scheduled'
  },
  {
    id: '6',
    patientName: 'Roberto Vargas',
    patientEmail: 'roberto.vargas@email.com',
    doctorName: 'Dr. Roberto Mendoza',
    date: '2025-07-23T13:00:00.000Z',
    duration: 30,
    type: 'follow-up',
    notes: 'Seguimiento tratamiento de alergias',
    status: 'confirmed',
    PK: 'APPOINTMENT#6',
    SK: 'APPOINTMENT#6',
    GSI1PK: 'roberto.vargas@email.com',
    GSI1SK: 'roberto.vargas@email.com',
    GSI2PK: 'Dr. Roberto Mendoza',
    GSI2SK: '2025-07-23T13:00:00.000Z',
    GSI3PK: 'confirmed',
    GSI3SK: 'confirmed'
  },
  {
    id: '7',
    patientName: 'Ana Rodríguez',
    patientEmail: 'ana.rodriguez@email.com',
    doctorName: 'Dra. Carmen Ruiz',
    date: '2025-07-27T10:30:00.000Z',
    duration: 60,
    type: 'consultation',
    notes: 'Consulta ginecológica de rutina',
    status: 'scheduled',
    PK: 'APPOINTMENT#7',
    SK: 'APPOINTMENT#7',
    GSI1PK: 'ana.rodriguez@email.com',
    GSI1SK: 'ana.rodriguez@email.com',
    GSI2PK: 'Dra. Carmen Ruiz',
    GSI2SK: '2025-07-27T10:30:00.000Z',
    GSI3PK: 'scheduled',
    GSI3SK: 'scheduled'
  },
  {
    id: '8',
    patientName: 'Luis Pérez',
    patientEmail: 'luis.perez@email.com',
    doctorName: 'Dr. Carlos Rodríguez',
    date: '2025-07-28T15:00:00.000Z',
    duration: 45,
    type: 'emergency',
    notes: 'Dolor de cabeza intenso y mareos',
    status: 'scheduled',
    PK: 'APPOINTMENT#8',
    SK: 'APPOINTMENT#8',
    GSI1PK: 'luis.perez@email.com',
    GSI1SK: 'luis.perez@email.com',
    GSI2PK: 'Dr. Carlos Rodríguez',
    GSI2SK: '2025-07-28T15:00:00.000Z',
    GSI3PK: 'scheduled',
    GSI3SK: 'scheduled'
  }
];

// Seed Orders
async function seedOrders() {
  console.log('Seeding orders...');
  
  for (const order of sampleOrders) {
    try {
      const command = new PutCommand({
        TableName: ORDERS_TABLE,
        Item: order
      });
      
      await docClient.send(command);
      console.log(`✅ Order ${order.id} seeded successfully`);
    } catch (error) {
      console.error(`❌ Error seeding order ${order.id}:`, error);
    }
  }
  
  console.log('Orders seeding completed!');
}

// Seed Appointments
async function seedAppointments() {
  console.log('Seeding appointments...');
  
  for (const appointment of sampleAppointments) {
    try {
      const command = new PutCommand({
        TableName: APPOINTMENTS_TABLE,
        Item: appointment
      });
      
      await docClient.send(command);
      console.log(`✅ Appointment ${appointment.id} seeded successfully`);
    } catch (error) {
      console.error(`❌ Error seeding appointment ${appointment.id}:`, error);
    }
  }
  
  console.log('Appointments seeding completed!');
}

// Main function
async function seedData() {
  console.log('🚀 Starting data seeding...');
  console.log(`Orders Table: ${ORDERS_TABLE}`);
  console.log(`Appointments Table: ${APPOINTMENTS_TABLE}`);
  
  try {
    await seedOrders();
    await seedAppointments();
    console.log('🎉 All data seeded successfully!');
  } catch (error) {
    console.error('❌ Error during seeding:', error);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  seedData();
}

module.exports = { seedData, seedOrders, seedAppointments }; 