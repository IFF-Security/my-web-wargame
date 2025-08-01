const express = require('express');
const app = express();
const port = 3000;

app.use(express.static('public'));

let user_data = {};

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.post('/', (req, res) => {
  res.send('POST /');
});

// '/set' 엔드포인트는 GET 메서드로 username, key, value 인자를 받아 user_data[username][key] = value으로 저장
// '/get' 엔드포인트는 GET 메서드로 username, key 인자를 받아 user_data[username][key]를 출력
// '/show_all' 엔드포인트는 user_data의 모든 값을 출력

app.get('/set/:username/:key/:value', (req, res) => {
  const { username, key, value } = req.params;
  if (!user_data[username]) user_data[username] = {};
  user_data[username][key] = value;
  res.send(`OK! set user_data[${username}][${key}] to ${value}.`);
});

app.get('/get/:username/:key', (req, res) => {
  const { username, key } = req.params;
  res.send(user_data[username][key]);
});

app.get('/show_all', (req, res) => {
  res.send(JSON.stringify(user_data, undefined, 2));
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
