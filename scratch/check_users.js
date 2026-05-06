const { Client } = require('pg');

const client = new Client({
  connectionString: "postgresql://ciap:ciap_dev_password@localhost:5432/ciap"
});

async function checkUsers() {
  try {
    await client.connect();
    const res = await client.query('SELECT id, name, email, role FROM users');
    console.log('Users in DB:', res.rows);
    
    const profiles = await client.query('SELECT user_id, display_name FROM user_profiles');
    console.log('Profiles in DB:', profiles.rows);
  } catch (err) {
    console.error(err);
  } finally {
    await client.end();
  }
}

checkUsers();
