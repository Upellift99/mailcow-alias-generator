# Multi-User Configuration

This feature allows you to have multiple users with different passwords and default redirect addresses.

## Configuration

### Setting up config.json

Your `config.json` file must contain a `users` section with all your users:

```json
{
  "mailcow_url": "https://mail.example.com",
  "api_key": "YOUR_MAILCOW_API_KEY_HERE",
  "domain": "example.com",
  "sogo_visible": true,
  "altcha_enabled": false,
  "altcha_hmac_key": "head -c32 /dev/urandom | base64",
  "port": 5000,
  "users": {
    "user1": {
      "password": "password_user1",
      "default_redirect": "user1@example.com",
      "description": "First user"
    },
    "user2": {
      "password": "password_user2", 
      "default_redirect": "user2@example.com",
      "description": "Second user"
    }
  }
}
```

## How it works

### Authentication

- Each user has their own password defined in the `users` section
- During login, the application automatically identifies the user based on the provided password
- User information is stored in the session for personalized experience

### Default redirect address

- Each user has their own default redirect address
- This address is automatically pre-filled in the alias creation form
- Users can still modify this address for specific aliases

### User interface

- The interface displays the name/description of the connected user
- Each user sees their own default redirect address
- Personalized experience based on user configuration

## Usage example

1. **User 1** logs in with `password_user1`
   - Sees `user1@example.com` as default redirect address
   - Interface displays "First user"

2. **User 2** logs in with `password_user2`
   - Sees `user2@example.com` as default redirect address
   - Interface displays "Second user"

## Adding additional users

To add a new user, simply add a new entry in the `users` section:

```json
"users": {
  "user1": {
    "password": "password_user1",
    "default_redirect": "user1@example.com",
    "description": "First user"
  },
  "user2": {
    "password": "password_user2", 
    "default_redirect": "user2@example.com",
    "description": "Second user"
  },
  "user3": {
    "password": "password_user3",
    "default_redirect": "user3@example.com",
    "description": "Third user"
  }
}
```

## Security

- Each user can only see their own information
- Passwords are stored in plain text in the configuration file
- Make sure the `config.json` file has proper permissions (read-only for the application user)
- Use strong, unique passwords for each user
- Consider using environment variables for sensitive data in production

## User management

### User properties

Each user entry supports the following properties:

- `password` (required): The user's login password
- `default_redirect` (required): Default email address for alias redirection
- `description` (optional): Human-readable description displayed in the interface

### Best practices

- Use descriptive user IDs (e.g., "john", "admin", "support")
- Use strong passwords for each user
- Set meaningful descriptions to easily identify users
- Use domain-specific redirect addresses when possible