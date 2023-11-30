# ChatGPT-with-WhatsApp

This repository contains a simple Flask application that serves as a WhatsApp AI chatbot powered by OpenAI's GPT-3.5-turbo model.

## Prerequisites

Before running the application, make sure you have the following prerequisites:

- [Meta Developers Account](https://developers.facebook.com/)
- [OpenAI API Key](https://platform.openai.com/account/api-keys)

Follow these steps to set up the Meta WhatsApp AI Chatbot:

1. **Create a Meta Developers Account:**
   - Go to [Meta Developers](https://developers.meta.com/) and create a new business app.

2. **Add WhatsApp Product Service:**
   - Add a product service named `whatsapp` in your Meta business app.
   - Obtain the temporary access token for the `whatsapp` service (this is the `WHATSAPP_TOKEN`).

3. **Verify Phone Number:**
   - Add your recipient phone number and verify it.

4. **Configure Webhooks:**
   - Go to the webhook configuration section.
   - Provide the URL and `verify_token` for your Flask app.

5. **Setup Code Server on Glitch:**
   - Host this code server on [Glitch](https://glitch.com/).
   - Add all the required environment variables in the `.env` file on Glitch.

6. **Run the Program:**
   - Start the Flask app on Glitch.

7. **Add Glitch Site's URL for Verification:**
   - Add your Glitch site's URL followed by `/webhook` (e.g., `https://your-glitch-app.glitch.me/webhook`) for verification in the Meta app.

8. **Subscribe to Webhook Fields:**
   - Subscribe to the necessary webhook fields, such as `messages`, etc., as required by your application.

9. **Run Without Issues:**
   - The application

## Setup of server

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/your-username/your-repository.git
    cd your-repository
    ```

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the root directory and set the following variables:

    ```env
    VERIFY_TOKEN=your_verify_token
    WHATSAPP_TOKEN=your_whatsapp_token
    OPENAI_API_KEY=your_openai_api_key
    ```

    Replace `your_verify_token`, `your_whatsapp_token`, and `your_openai_api_key` with your actual values.

## Running the Application

Run the Flask application with the following command:

```bash
python app.py
