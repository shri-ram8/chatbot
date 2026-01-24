const express = require("express");
const cors = require("cors");
const { Pool } = require("pg");

const app = express();
app.use(cors());
app.use(express.json());

// PostgreSQL connection
const pool = new Pool({
  user: "postgres",
  host: "localhost",
  database: "chatbotdb",
  password: "Batmannn@08", 
  port: 5433
});

// Simple intent + DB search
app.post("/chat", async (req, res) => {
  const userMsg = req.body.message.toLowerCase();
  let reply = "";

  // Dynamic answers
  if (userMsg.includes("date")) {
    reply = new Date().toDateString();
  } 
  else if (userMsg.includes("time")) {
    reply = new Date().toLocaleTimeString();
  }
  else {
    // Search in database
    const result = await pool.query(
      "SELECT answer FROM knowledge WHERE $1 ILIKE '%' || question || '%'",
      [userMsg]
    );

    if (result.rows.length > 0) {
      reply = result.rows[0].answer;
    } else {
      reply = "Sorry, I don't know this yet. I am still learning.";
    }
  }

  res.json({ answer: reply });
});

// Start server
app.listen(3000, () => {
  console.log("Jarvis chatbot backend running on http://localhost:3000");
});
