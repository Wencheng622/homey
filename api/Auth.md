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

````


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

````

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

### Authentication

Required.

Role: `admin`

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

### Business Rules

- Only existing admins can send admin invitations
- One email can have multiple invitation records over time
- Only one active pending invitation is allowed per email
- Creating a new invitation revokes previous pending invitations for the same email
- Invitation token is short-lived
- Invitation token is sent by email and not returned in the API response
- If the email already belongs to an existing user, the system should reject the invitation
