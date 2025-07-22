const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, PutCommand } = require('@aws-sdk/lib-dynamodb');

// Initialize DynamoDB client
const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);

// Table names from environment variables
const ORDERS_TABLE = process.env.ORDERS_TABLE || 'nova-sonic-server-app-demo-orders';
const APPOINTMENTS_TABLE = process.env.APPOINTMENTS_TABLE || 'nova-sonic-server-app-demo-appointments';

// Helper function to create dates in Argentina timezone (UTC-3)
function createArgentinaDate(year, month, day, hour = 0, minute = 0, second = 0) {
  // Create date in Argentina timezone (UTC-3)
  const date = new Date(year, month - 1, day, hour, minute, second);
  const argentinaOffset = -3 * 60; // UTC-3 in minutes
  const utcTime = date.getTime() + (date.getTimezoneOffset() * 60000);
  const argentinaTime = new Date(utcTime + (argentinaOffset * 60000));
  
  // Format as ISO string with Argentina timezone offset (-03:00)
  const year_str = argentinaTime.getFullYear();
  const month_str = String(argentinaTime.getMonth() + 1).padStart(2, '0');
  const day_str = String(argentinaTime.getDate()).padStart(2, '0');
  const hour_str = String(argentinaTime.getHours()).padStart(2, '0');
  const minute_str = String(argentinaTime.getMinutes()).padStart(2, '0');
  const second_str = String(argentinaTime.getSeconds()).padStart(2, '0');
  
  return `${year_str}-${month_str}-${day_str}T${hour_str}:${minute_str}:${second_str}.000-03:00`;
}

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
    createdAt: createArgentinaDate(2025, 7, 15, 10, 30),
    updatedAt: createArgentinaDate(2025, 7, 15, 10, 30),
    estimatedDelivery: createArgentinaDate(2025, 7, 20),
    PK: 'ORDER#1',
    SK: 'ORDER#1',
    GSI1PK: 'maria.gonzalez@email.com',
    GSI1SK: `pending#${createArgentinaDate(2025, 7, 15, 10, 30)}`
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
    createdAt: createArgentinaDate(2025, 7, 14, 14, 15),
    updatedAt: createArgentinaDate(2025, 7, 16, 9, 45),
    trackingNumber: 'TRK789456123',
    PK: 'ORDER#2',
    SK: 'ORDER#2',
    GSI1PK: 'carlos.mendoza@email.com',
    GSI1SK: `processing#${createArgentinaDate(2025, 7, 14, 14, 15)}`
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
    createdAt: createArgentinaDate(2025, 7, 13, 11, 20),
    updatedAt: createArgentinaDate(2025, 7, 17, 16, 30),
    trackingNumber: 'TRK456789321',
    estimatedDelivery: createArgentinaDate(2025, 7, 19),
    PK: 'ORDER#3',
    SK: 'ORDER#3',
    GSI1PK: 'ana.rodriguez@email.com',
    GSI1SK: `shipped#${createArgentinaDate(2025, 7, 13, 11, 20)}`
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
    createdAt: createArgentinaDate(2025, 7, 10, 8, 45),
    updatedAt: createArgentinaDate(2025, 7, 12, 14, 20),
    trackingNumber: 'TRK123789456',
    PK: 'ORDER#4',
    SK: 'ORDER#4',
    GSI1PK: 'luis.fernandez@email.com',
    GSI1SK: `delivered#${createArgentinaDate(2025, 7, 10, 8, 45)}`
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
    createdAt: createArgentinaDate(2025, 7, 8, 16, 30),
    updatedAt: createArgentinaDate(2025, 7, 9, 10, 15),
    PK: 'ORDER#5',
    SK: 'ORDER#5',
    GSI1PK: 'carmen.silva@email.com',
    GSI1SK: `cancelled#${createArgentinaDate(2025, 7, 8, 16, 30)}`
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
    createdAt: createArgentinaDate(2025, 7, 18, 12, 0),
    updatedAt: createArgentinaDate(2025, 7, 18, 12, 0),
    estimatedDelivery: createArgentinaDate(2025, 7, 23),
    PK: 'ORDER#6',
    SK: 'ORDER#6',
    GSI1PK: 'roberto.vargas@email.com',
    GSI1SK: `pending#${createArgentinaDate(2025, 7, 18, 12, 0)}`
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
    createdAt: createArgentinaDate(2025, 7, 17, 9, 30),
    updatedAt: createArgentinaDate(2025, 7, 19, 15, 45),
    trackingNumber: 'TRK987321654',
    PK: 'ORDER#7',
    SK: 'ORDER#7',
    GSI1PK: 'elena.martinez@email.com',
    GSI1SK: `processing#${createArgentinaDate(2025, 7, 17, 9, 30)}`
  }
];

// Sample Appointments Data - Updated with recent dates from July 2025 onwards
const sampleAppointments = [
  {
    id: '1',
    patientName: 'María González',
    patientEmail: 'maria.gonzalez@email.com',
    doctorName: 'Dr. Carlos Rodríguez',
    date: createArgentinaDate(2025, 7, 22, 10, 0),
    duration: 30,
    type: 'consultation',
    notes: 'Consulta de rutina - Control anual',
    status: 'scheduled',
    PK: 'APPOINTMENT#1',
    SK: 'APPOINTMENT#1',
    GSI1PK: 'maria.gonzalez@email.com',
    GSI1SK: 'maria.gonzalez@email.com',
    GSI2PK: 'Dr. Carlos Rodríguez',
    GSI2SK: createArgentinaDate(2025, 7, 22, 10, 0),
    GSI3PK: 'scheduled',
    GSI3SK: 'scheduled'
  },
  {
    id: '2',
    patientName: 'Luis Fernández',
    patientEmail: 'luis.fernandez@email.com',
    doctorName: 'Dra. Ana López',
    date: createArgentinaDate(2025, 7, 24, 14, 30),
    duration: 45,
    type: 'follow-up',
    notes: 'Seguimiento post-cirugía de rodilla',
    status: 'confirmed',
    PK: 'APPOINTMENT#2',
    SK: 'APPOINTMENT#2',
    GSI1PK: 'luis.fernandez@email.com',
    GSI1SK: 'luis.fernandez@email.com',
    GSI2PK: 'Dra. Ana López',
    GSI2SK: createArgentinaDate(2025, 7, 24, 14, 30),
    GSI3PK: 'confirmed',
    GSI3SK: 'confirmed'
  },
  {
    id: '3',
    patientName: 'Carmen Silva',
    patientEmail: 'carmen.silva@email.com',
    doctorName: 'Dr. Roberto Mendoza',
    date: createArgentinaDate(2025, 7, 25, 9, 0),
    duration: 60,
    type: 'emergency',
    notes: 'Dolor agudo en el pecho - Requiere evaluación inmediata',
    status: 'scheduled',
    PK: 'APPOINTMENT#3',
    SK: 'APPOINTMENT#3',
    GSI1PK: 'carmen.silva@email.com',
    GSI1SK: 'carmen.silva@email.com',
    GSI2PK: 'Dr. Roberto Mendoza',
    GSI2SK: createArgentinaDate(2025, 7, 25, 9, 0),
    GSI3PK: 'scheduled',
    GSI3SK: 'scheduled'
  },
  {
    id: '4',
    patientName: 'Carlos Mendoza',
    patientEmail: 'carlos.mendoza@email.com',
    doctorName: 'Dr. Carlos Rodríguez',
    date: createArgentinaDate(2025, 7, 22, 11, 0),
    duration: 30,
    type: 'routine',
    notes: 'Control de presión arterial y diabetes',
    status: 'confirmed',
    PK: 'APPOINTMENT#4',
    SK: 'APPOINTMENT#4',
    GSI1PK: 'carlos.mendoza@email.com',
    GSI1SK: 'carlos.mendoza@email.com',
    GSI2PK: 'Dr. Carlos Rodríguez',
    GSI2SK: createArgentinaDate(2025, 7, 22, 11, 0),
    GSI3PK: 'confirmed',
    GSI3SK: 'confirmed'
  },
  {
    id: '5',
    patientName: 'Elena Martínez',
    patientEmail: 'elena.martinez@email.com',
    doctorName: 'Dra. Ana López',
    date: createArgentinaDate(2025, 7, 26, 16, 0),
    duration: 45,
    type: 'consultation',
    notes: 'Primera consulta - Evaluación general',
    status: 'scheduled',
    PK: 'APPOINTMENT#5',
    SK: 'APPOINTMENT#5',
    GSI1PK: 'elena.martinez@email.com',
    GSI1SK: 'elena.martinez@email.com',
    GSI2PK: 'Dra. Ana López',
    GSI2SK: createArgentinaDate(2025, 7, 26, 16, 0),
    GSI3PK: 'scheduled',
    GSI3SK: 'scheduled'
  },
  {
    id: '6',
    patientName: 'Roberto Vargas',
    patientEmail: 'roberto.vargas@email.com',
    doctorName: 'Dr. Roberto Mendoza',
    date: createArgentinaDate(2025, 7, 23, 13, 0),
    duration: 30,
    type: 'follow-up',
    notes: 'Seguimiento tratamiento de alergias',
    status: 'confirmed',
    PK: 'APPOINTMENT#6',
    SK: 'APPOINTMENT#6',
    GSI1PK: 'roberto.vargas@email.com',
    GSI1SK: 'roberto.vargas@email.com',
    GSI2PK: 'Dr. Roberto Mendoza',
    GSI2SK: createArgentinaDate(2025, 7, 23, 13, 0),
    GSI3PK: 'confirmed',
    GSI3SK: 'confirmed'
  },
  {
    id: '7',
    patientName: 'Ana Rodríguez',
    patientEmail: 'ana.rodriguez@email.com',
    doctorName: 'Dra. Carmen Ruiz',
    date: createArgentinaDate(2025, 7, 27, 10, 30),
    duration: 60,
    type: 'consultation',
    notes: 'Consulta ginecológica de rutina',
    status: 'scheduled',
    PK: 'APPOINTMENT#7',
    SK: 'APPOINTMENT#7',
    GSI1PK: 'ana.rodriguez@email.com',
    GSI1SK: 'ana.rodriguez@email.com',
    GSI2PK: 'Dra. Carmen Ruiz',
    GSI2SK: createArgentinaDate(2025, 7, 27, 10, 30),
    GSI3PK: 'scheduled',
    GSI3SK: 'scheduled'
  },
  {
    id: '8',
    patientName: 'Luis Pérez',
    patientEmail: 'luis.perez@email.com',
    doctorName: 'Dr. Carlos Rodríguez',
    date: createArgentinaDate(2025, 7, 28, 15, 0),
    duration: 45,
    type: 'emergency',
    notes: 'Dolor de cabeza intenso y mareos',
    status: 'scheduled',
    PK: 'APPOINTMENT#8',
    SK: 'APPOINTMENT#8',
    GSI1PK: 'luis.perez@email.com',
    GSI1SK: 'luis.perez@email.com',
    GSI2PK: 'Dr. Carlos Rodríguez',
    GSI2SK: createArgentinaDate(2025, 7, 28, 15, 0),
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