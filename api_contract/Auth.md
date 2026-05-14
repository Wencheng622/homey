# Auth API

Base URL:

`/api/v1/auth/`

---

## Register User

`POST /api/v1/auth/register/`

### Description

Create a new user account using email and password authentication.

### Authentication

Not required.

### Request Body

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "role": "tenant"
}
```

### Request Field Notes

- `email` must be unique
- `password` must meet security requirements
- `role` can only be:
  - `tenant`
  - `landlord`

### Success Response

Status: `201 Created`

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "role": "tenant",
  "status": "email_unverified",
  "is_email_verified": false,
  "created_at": "2026-05-08T12:00:00Z"
}
```

### Error Responses

#### 400 Bad Request

Invalid request data.

```json
{
  "email": ["A user with this email already exists."]
}
```

#### 403 Forbidden

Attempt to self-register an admin account.

```json
{
  "detail": "Admin accounts cannot be self-registered."
}
```

### Business Rules

- Email addresses must be unique
- Passwords are securely hashed before storage
- Newly registered users start with `email_unverified` status
- Email verification is required before full account activation
- Only `tenant` and `landlord` roles can self-register
- `admin` accounts must be created through invitation flow

### Side Effects / Data Changes

- Create one record in `users`
- Automatically create one linked record in `profiles`

## Request Password Reset

`POST /api/v1/auth/password-reset/request/`

### Description

Request a password reset email. If the email exists, the system generates a short-lived password reset token and sends a reset link to the user's email.

### Authentication

Not required.

### Request Body

```json
{
  "email": "user@example.com"
}
```

### Success Response

Status: `200 OK`

```json
{
  "detail": "If this email exists, a password reset link has been sent."
}
```

### Business Rules

- This endpoint does not reveal whether the email exists
- Token should be short-lived, for example 15–30 minutes
- Previous unused password reset tokens for this user should be revoked before creating a new token
- The reset link should contain the token

### Side Effects / Data Changes

- Create one record in `password_reset_tokens`
- Revoke previous unused reset tokens for the same user
- Send password reset email

## Confirm Password Reset

`POST /api/v1/auth/password-reset/confirm/`

### Description

Reset the user's password using a valid password reset token.

### Authentication

Not required.

### Request Body

```json
{
  "token": "reset-token-string",
  "new_password": "NewSecurePassword123!"
}
````

### Success Response

Status: `200 OK`

```json
{
  "detail": "Password has been reset successfully."
}
```

### Error Responses

#### 400 Bad Request

Invalid or expired token.

```json
{
  "detail": "Invalid or expired password reset token."
}
```

#### 400 Bad Request

Weak password.

```json
{
  "new_password": ["Password does not meet security requirements."]
}
```

### Business Rules

- Token must exist
- Token must not be expired
- Token must not be used
- Token must not be revoked
- New password must meet security requirements
- After successful reset, the token is marked as used
- User password is securely hashed before storage

### Side Effects / Data Changes

- Update `users.password_hash`
- Set `password_reset_tokens.used_at`
- Revoke other unused reset tokens for the same user

## Login User

`POST /api/v1/auth/login/`

### Description

Authenticate a user with email and password, and return access and refresh tokens.

### Authentication

Not required.

### Request Body

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
````

### Success Response

Status: `200 OK`

```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "tenant",
    "status": "email_unverified",
    "is_email_verified": false
  }
}
```

### Error Responses

#### 400 Bad Request

Missing or invalid request data.

```json
{
  "email": ["This field is required."]
}
```

#### 401 Unauthorized

Invalid email or password.

```json
{
  "detail": "Invalid email or password."
}
```

#### 403 Forbidden

Account is suspended.

```json
{
  "detail": "This account has been suspended."
}
```

### Business Rules

- Login requires a valid email and password
- The response must not reveal whether the email or password is incorrect
- Suspended users cannot log in
- Password is checked against the stored password hash
- Access token should be short-lived
- Refresh token should be longer-lived and can be used to request a new access token

### Side Effects / Data Changes

- Issue one access token
- Issue one refresh token
- Optionally update `users.last_login_at`

## Send Admin Invitation

`POST /api/v1/admin/invitations/`

### Description

Allow an existing admin to invite a new admin by email.

The backend generates a secure invitation token, revokes previous active invitations for the same email, stores the invitation record, and sends an invitation email containing a secure invitation link.

### Authentication

Required.

Role: `admin`

Authentication method:

- JWT
- HttpOnly Cookie
- CSRF protection required

### Request Body

```json
{
  "email": "newadmin@example.com"
}
```

### Success Response

Status: `201 Created`

```json
{
  "id": "uuid",
  "email": "newadmin@example.com",
  "status": "pending",
  "expires_at": "2026-05-09T12:00:00Z"
}
```

### Error Responses

#### 400 Bad Request

```json
{
  "email": ["A valid email address is required."]
}
```

#### 403 Forbidden

```json
{
  "detail": "Only admins can send invitations."
}
```

#### 409 Conflict

```json
{
  "detail": "An active invitation already exists for this email."
}
```

#### 409 Conflict

```json
{
  "detail": "A user with this email already exists."
}
```

### Business Rules

- Only existing admins can send admin invitations
- Admin accounts cannot be created through normal registration
- One email can have multiple invitation records over time
- Only one active pending invitation is allowed per email at a time
- Creating a new invitation revokes previous pending invitations for the same email
- Invitation tokens must be short-lived
- Invitation tokens must not be returned in API responses
- Invitation links are sent by email
- Existing registered users cannot be invited again

### Side Effects / Data Changes

- Generate a secure invitation token
- Revoke previous pending invitations for the same email
- Create one record in `admin_invitations`
- Send invitation email containing the invitation link

## Validate Admin Invitation

`POST /api/v1/admin/invitations/validate/`

### Description

Validate whether an admin invitation token is still valid before allowing the invited user to continue registration.

### Authentication

Not required.

### Request Body

```json
{
  "token": "secure-invitation-token"
}
```

### Success Response

Status: `200 OK`

```json
{
  "email": "newadmin@example.com",
  "status": "valid",
  "expires_at": "2026-05-09T12:00:00Z"
}
```

### Error Responses

#### 400 Bad Request

```json
{
  "detail": "Invalid or expired invitation token."
}
```

### Business Rules

- Token must exist
- Token must not be expired
- Token must not be revoked
- Token must not already be accepted
- Token must not already be rejected
- If valid, frontend may display the admin onboarding form
- Invitation email should be displayed but must not be editable

## Accept Admin Invitation

`POST /api/v1/admin/invitations/accept/`

### Description

Accept a valid admin invitation and create an active admin account.

### Authentication

Not required.

### Request Body

```json
{
  "token": "secure-invitation-token",
  "password": "SecurePassword123!",
  "display_name": "Eleana Guan"
}
```

### Success Response

Status: `201 Created`

```json
{
  "user": {
    "id": "uuid",
    "email": "newadmin@example.com",
    "role": "admin",
    "status": "active",
    "is_email_verified": true
  }
}
```

### Response Cookies

```http
Set-Cookie: access_token=<jwt-access-token>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=900

Set-Cookie: refresh_token=<jwt-refresh-token>; HttpOnly; Secure; SameSite=Lax; Path=/api/v1/auth/refresh/; Max-Age=604800
```

### Error Responses

#### 400 Bad Request

```json
{
  "detail": "Invalid or expired invitation token."
}
```

#### 400 Bad Request

```json
{
  "password": ["Password does not meet security requirements."]
}
```

#### 409 Conflict

```json
{
  "detail": "A user with this email already exists."
}
```

### Business Rules

- Token must exist
- Token must not be expired
- Token must not be revoked
- Token must not already be accepted
- Invitation email determines the new admin account email
- Invitation email cannot be changed during onboarding
- Password must satisfy security requirements
- Accepting an invitation immediately creates an active admin account
- Invitation-based admin onboarding automatically treats the email as verified
- Accepted invitations cannot be reused
- JWT tokens are returned through secure HttpOnly cookies
- CSRF protection is required

### Side Effects / Data Changes

- Create one record in `users`
- Create one linked record in `profiles`
- Set `admin_invitations.status` to `accepted`
- Set `admin_invitations.accepted_at`
- Set `admin_invitations.accepted_user_id`
- Generate JWT access token
- Generate JWT refresh token
- Set secure HttpOnly authentication cookies

## Reject Admin Invitation

`POST /api/v1/admin/invitations/reject/`

### Description

Reject a valid admin invitation without creating an admin account.

### Authentication

Not required.

### Request Body

```json
{
  "token": "secure-invitation-token"
}
```

### Success Response

Status: `200 OK`

```json
{
  "detail": "Invitation has been rejected."
}
```

### Error Responses

#### 400 Bad Request

```json
{
  "detail": "Invalid or expired invitation token."
}
```

### Business Rules

- Token must exist
- Token must not be expired
- Token must not be revoked
- Token must not already be accepted
- Token must not already be rejected
- Rejecting an invitation does not create a user account
- Rejected invitations cannot be reused
- A new invitation can be sent to the same email later

### Side Effects / Data Changes

- Set `admin_invitations.status` to `rejected`
- Set `admin_invitations.rejected_at`

## Request Email Verification

`POST /api/v1/auth/email-verification/request/`

### Description

Generate a short-lived email verification token and send a verification link to the current user's email address.

### Authentication

Required.

Authentication method:

- JWT
- Secure HttpOnly Cookie
- CSRF protection required

### Request Body

```json
{}
````

### Success Response

Status: `200 OK`

```json
{
  "detail": "Verification email has been sent."
}
```

### Error Responses

#### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 409 Conflict

```json
{
  "detail": "Email is already verified."
}
```

### Business Rules

- Only logged-in users can request email verification
- Only users with `is_email_verified=false` can request verification
- Token must be short-lived
- Creating a new verification token revokes previous unused verification tokens for the same user
- Verification token must not be returned in the API response
- Verification link is sent by email

### Side Effects / Data Changes

- Generate a secure email verification token
- Revoke previous unused verification tokens for the same user
- Create one record in `email_verification_tokens`
- Send verification email containing the verification link

## Confirm Email Verification

`POST /api/v1/auth/email-verification/confirm/`

### Description

Verify the user's email address using a valid email verification token.

### Authentication

Not required.

### Request Body

```json
{
  "token": "secure-email-verification-token"
}
```

### Success Response

Status: `200 OK`

```json
{
  "detail": "Email has been verified successfully."
}
```

### Error Responses

#### 400 Bad Request

```json
{
  "detail": "Invalid or expired email verification token."
}
```

### Business Rules

- Token must exist
- Token must not be expired
- Token must not be revoked
- Token must not already be used
- Once verified, the user account becomes active
- Used verification tokens cannot be reused

### Side Effects / Data Changes

- Set `users.is_email_verified` to `true`
- Set `users.status` to `active`
- Set `email_verification_tokens.used_at`
- Revoke other unused email verification tokens for the same user
