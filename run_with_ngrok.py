from pyngrok import ngrok
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    ngrok_domain = os.environ.get("NGROK_DOMAIN")
    if ngrok_domain:
        public_url = ngrok.connect(
            port,
            bind_tls=True,
            domain=ngrok_domain
        )
    else:
        public_url = ngrok.connect(port, bind_tls=True)
    print(f" * ngrok tunnel available at: {public_url}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
