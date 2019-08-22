#======================================== CODES =============================================================

#Codes
USERNOTEXIST 	   = 404
AUTH_SUCCESS 	   = 200
INCORRECT_PASSWORD = 401
USER_INACTIVE      = 402


#Code Containers
SUCESS_CALLS  = [AUTH_SUCCESS]
FAILED_CALLS  = [USERNOTEXIST,INCORRECT_PASSWORD,USER_INACTIVE]


#======================================= MESSAGES =============================================================

#Messages
INVALID_LINK       = "Activation link is Invalid !"
ACCOUNT_ACTIVATED  = "Email Verification Success! Please Login here"
ACCOUNT_INACTIVE   = "Your Account is InActive !, Please Activate"
USERNOT_FOUND      = "User not found !"
VERFMAIL_SENT      = "Verification mail sent succssfully !"
RESET_PASSWORDLINK = "Password reset link sent to your mail, please follow up that"
INVALID_PASSWORD   = "Invalid Password !"
PASSWORD_RESET_SUCCESS   = "Password has been changed"