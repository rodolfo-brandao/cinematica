-- NOTE: The "iso_alpha3_code" column indicates a three-letter code defined in ISO 3166-1 to
-- represent countries, dependent territories and special areas of geographical interest.

USE Cinematica;

INSERT INTO country (id, [name], iso_alpha3_code, created_on, updated_on, is_disabled)
VALUES ('989adb5a-3434-4239-bfaa-8752dcd18e9b', 'United States of America', 'USA', GETDATE(), NULL, 0);

INSERT INTO country (id, [name], iso_alpha3_code, created_on, updated_on, is_disabled)
VALUES ('90aa24a3-8cf4-48eb-8164-60351c748ebe', 'Japan', 'JPN', GETDATE(), NULL, 0);

INSERT INTO country (id, [name], iso_alpha3_code, created_on, updated_on, is_disabled)
VALUES ('0d4d1993-9633-4f18-a7b8-4b0f24be18ef', 'Brazil', 'BRA', GETDATE(), null, 0);

INSERT INTO country (id, [name], iso_alpha3_code, created_on, updated_on, is_disabled)
VALUES ('3317dd62-b24f-41f2-859f-3aa71525c3ee', 'France', 'FRA', GETDATE(), null, 0);