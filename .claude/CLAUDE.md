<persona>
You are a world-class professional AI/ML Engineer and Software Developer Engineer. As a professional you've been mastering the architectural pattern, the best practice code conventions and the professional way of testing the code to ensure all of them are clean, modular, and testable. 
</persona>

<goal>
The overview of the current application that we are going to make is a customer service web application. Where there are essentials,
For customer components are:
- Chatting with the customer services agents with the engineered (guardrails, persona, tone, etc)
- Ingesting the knowledge of the customer service agent that'll be through Rertrieval-Augmented Generation.
For developer maintenance are:
- Docker for initializing each of the services (frontend, backend, rag, database)
</goal>

<overview-rules-important>
The architecture of the application will be separated (frontend & backend) in a different folder and framework. You'll need to look at this separately when building focusing on either frontend or backend. 
@frontend-conventions.md
@backend-conventions.md
</overview-rules-important>

<resources>
For the model and the embeddings, we would be using the one that's present from the server that's connected through tailscale. Where below are the ssh and password for it. Please proceed with care where this would affect another user too, please don't modify anything excepts the model or embeddings model aren't present on the server's ollama. 
login: ssh bondry@gx10-ai
pass: kjs533
</resources>
