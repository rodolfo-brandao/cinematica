USE Cinematica;

-- (for testing purposes only, the raw password is "12345678")
INSERT INTO [user] (id, username, email, [password], password_salt, [role], created_on, updated_on, is_disabled)
VALUES ('6a5561cc-df87-487e-9966-2bfa342525d4', 'gman', 'gman@blackmesa.com', 'fa0e123dee0f9abb81130fb62e3f729f', '09656a547f17764d3bac0c71', 'admin', GETDATE(), NULL, 0);

INSERT INTO [user] (id, username, email, [password], password_salt, [role], created_on, updated_on, is_disabled)
VALUES ('15e1b955-c9f8-4cfd-bcc0-223f2814358e', 'gordon-freeman', 'gfreeman@blackmesa.com', 'fa0e123dee0f9abb81130fb62e3f729f', '09656a547f17764d3bac0c71', 'user', GETDATE(), NULL, 0);