CREATE DATABASE chatbotdb;

\c chatbotdb;

CREATE TABLE knowledge (
  id SERIAL PRIMARY KEY,
  question TEXT,
  answer TEXT
);

INSERT INTO knowledge (question, answer) VALUES
('president of india', 'The President of India is Droupadi Murmu.'),
('prime minister of india', 'The Prime Minister of India is Narendra Modi.'),
('capital of india', 'The capital of India is New Delhi.'),
('who are you', 'I am Jarvis, your personal chatbot.'),
('what is your name', 'My name is Jarvis.');
