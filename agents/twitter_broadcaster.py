import tweepy
import os
from typing import Optional

class TwitterBroadcaster:
    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        self.api = self._setup_api() if all([
            self.api_key,
            self.api_secret,
            self.access_token,
            self.access_token_secret
        ]) else None
    
    def _setup_api(self) -> Optional[tweepy.API]:
        """
        Set up the Twitter API client.
        """
        try:
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            return tweepy.API(auth)
        except Exception as e:
            print(f"Error setting up Twitter API: {str(e)}")
            return None
    
    def post_update(self, message: str) -> bool:
        """
        Post an update to Twitter.
        
        Args:
            message (str): The message to post
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.api:
            print("Twitter API not configured. Skipping post.")
            return False
            
        try:
            self.api.update_status(message)
            return True
        except Exception as e:
            print(f"Error posting to Twitter: {str(e)}")
            return False
            
    def is_configured(self) -> bool:
        """
        Check if the Twitter API is properly configured.
        
        Returns:
            bool: True if configured, False otherwise
        """
        return self.api is not None
