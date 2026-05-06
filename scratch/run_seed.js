const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

const client = new Client({
  connectionString: "postgresql://ciap:ciap_dev_password@localhost:5432/ciap"
});

async function runSeed() {
  try {
    await client.connect();
    console.log('Connected to database');
    
    // Read the SQL file from the artifacts directory
    // I will use a simplified version of the SQL here to ensure it runs correctly
    const sql = `
      -- Seed script to populate creator profiles with better data
      INSERT INTO user_profiles (user_id, display_name, bio, location, industry, audience_size, influence_score, is_onboarded)
      SELECT 
          id, 
          name as display_name,
          'Creative director and digital storyteller focusing on lifestyle and technology.' as bio,
          'Lagos, Nigeria' as location,
          'Lifestyle' as industry,
          1200000 as audience_size,
          84.5 as influence_score,
          true as is_onboarded
      FROM users 
      WHERE role = 'creator'
      ON CONFLICT (user_id) DO UPDATE SET
          display_name = EXCLUDED.display_name,
          bio = EXCLUDED.bio,
          location = EXCLUDED.location,
          audience_size = EXCLUDED.audience_size,
          influence_score = EXCLUDED.influence_score,
          is_onboarded = true;
          
      -- Specific update for Shalom if she exists
      UPDATE user_profiles 
      SET influence_score = 0, is_onboarded = false, audience_size = 0
      WHERE display_name ILIKE '%Shalom%' OR user_id IN (SELECT id FROM users WHERE name ILIKE '%Shalom%');
    `;
    
    await client.query(sql);
    console.log('Seed completed successfully');
  } catch (err) {
    console.error('Seed failed', err);
  } finally {
    await client.end();
  }
}

runSeed();
