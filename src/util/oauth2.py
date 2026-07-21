import json
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwcrypto import jwt, jwk
from datetime import datetime, timedelta, timezone
import time
import base64

# 1. Point this to your existing login/token route
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user-authorize/with-jwt")

# 2. Set up your secret key using jwcrypto format
# (Ensure this matches the key you used to sign the token during login)
SECRET_KEY_STRING = "your-super-long-and-secure-secret-key-32-chars!!"


# 1. Encode the plain text string to base64url bytes
b64_key = base64.urlsafe_b64encode(SECRET_KEY_STRING.encode('utf-8')).decode('utf-8')

# 2. Clean up padding characters ("=") which jwcrypto dislikes
b64_key = b64_key.rstrip("=")

# 3. Pass the valid base64url string to the JWK constructor
signing_key = jwk.JWK(kty='oct', k=b64_key)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 2. Parse and verify the token using jwcrypto
        jwt_token = jwt.JWT(jwt=token, key=signing_key)
        
        # 3. Extract the JSON claims string and parse it to a dictionary
        claims = json.loads(jwt_token.claims)
        
        # 4. Extract your user ID from the claims (usually the 'sub' field)
        decoded_user_id = claims.get("sub")
        if decoded_user_id is None:
            raise credentials_exception
            
    except Exception as e: # Catches jwcrypto validation errors
        # 🚨 THIS IS CRITICAL: Check your terminal logs for this print statement!
        print(f"❌ Verification failed because: {str(e)}")
        raise credentials_exception

    print(decoded_user_id, "decoded_user_id")
        
    return int(decoded_user_id)

def create_access_token(user_id: int):
    # 1. Set the token expiration
    token_expiry = datetime.now(timezone.utc) + timedelta(days=1)
    # 2. Build claims ensuring 'sub' matches what your dependency expects
    payload = {
        "sub": str(user_id),  # standard JWT practice keeps sub as a string
        # "exp": int(time.time()) + 3600, # Expire in 1 hour
        "exp": int(token_expiry.timestamp()),
        "iat": int(time.time())
    }
    
    # 3. Sign the token using the exact same algorithm
    jwt_token = jwt.JWT(header={"alg": "HS256"}, claims=payload)
    jwt_token.make_signed_token(signing_key)
    access_token = jwt_token.serialize().encode('utf-8')
    return access_token
