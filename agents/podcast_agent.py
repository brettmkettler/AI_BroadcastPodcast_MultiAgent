from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
import os
from typing import Dict, Any

class PodcastAgent:
    def __init__(self, name: str, personality: str, voice_id: str):
        self.name = name
        self.personality = personality
        self.voice_id = voice_id
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Create the conversation prompt template
        template = f"""You are {self.name}, an AI podcast host with the following personality:
        {self.personality}
        
        Previous conversation:
        {{history}}
        
        Current topic or message:
        {{input}}
        
        Guidelines:
        - Speak naturally and conversationally
        - Keep responses concise (2-3 sentences)
        - Stay in character
        - Engage with your co-host's points
        - Add your unique perspective
        - Be engaging and dynamic
        - Focus on the current topic
        - Ask questions to keep the conversation flowing
        
        {self.name}'s response:"""
        
        self.prompt = PromptTemplate(
            input_variables=["history", "input"],
            template=template
        )
        
        # Create a memory store specific to this agent
        self.memory = ConversationBufferMemory(
            memory_key="history",
            input_key="input"
        )
        
        # Create the conversation chain
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=self.prompt,
            verbose=True
        )
        
    def generate_response(self, context: str) -> str:
        """
        Generate a response based on the conversation context.
        """
        try:
            response = self.conversation.predict(input=context)
            return response.strip()
        except Exception as e:
            print(f"Error generating response for {self.name}: {str(e)}")
            return f"I apologize, but I'm having trouble formulating my response. Let's continue our discussion."
    
    def get_memory_contents(self) -> str:
        """
        Get the contents of the agent's memory.
        """
        return self.memory.load_memory_variables({})["history"]
    
    def clear_memory(self):
        """
        Clear the agent's memory.
        """
        self.memory.clear()
