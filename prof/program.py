import random
import uuid
def generateUsername(userEmail : str) -> str:
    before_at = userEmail.split('@')[0]
    after_at = userEmail.split('@')[1]
    return "".join(random.choices(after_at+before_at, k=5))+ str(random.randint(0,100))
def productBuyingAbility(productPrice : float, requestAmount : float, balance : float):
    print(balance, (requestAmount * productPrice))
    if balance>= (requestAmount*productPrice):
        return True
    else:
        return False
def getProductToken() -> str:
    return str(uuid.uuid4())
if __name__ == '__main__':
    testEmail = "hello@world.com"
    print(generateUsername(testEmail))

