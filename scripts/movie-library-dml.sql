USE MovieLibrary;

-- USERS:
-- (for testing purposes only, the raw password value is "12345678")
INSERT INTO [user] (id, username, email, [password], password_salt, [role], created_on, updated_on, is_disabled)
VALUES ('6a5561cc-df87-487e-9966-2bfa342525d4', 'gman', 'gman@blackmesa.com', 'fa0e123dee0f9abb81130fb62e3f729f', '09656a547f17764d3bac0c71', 'admin', GETDATE(), NULL, 0);

INSERT INTO [user] (id, username, email, [password], password_salt, [role], created_on, updated_on, is_disabled)
VALUES ('15e1b955-c9f8-4cfd-bcc0-223f2814358e', 'gordon-freeman', 'gfreeman@blackmesa.com', 'fa0e123dee0f9abb81130fb62e3f729f', '09656a547f17764d3bac0c71', 'user', GETDATE(), NULL, 0);


-- COUNTRIES:
INSERT INTO country (id, [name], iso_alpha3_code, created_on, updated_on, is_disabled)
VALUES ('989adb5a-3434-4239-bfaa-8752dcd18e9b', 'United States of America', 'USA', GETDATE(), NULL, 0);

INSERT INTO country (id, [name], iso_alpha3_code, created_on, updated_on, is_disabled)
VALUES ('90aa24a3-8cf4-48eb-8164-60351c748ebe', 'Japan', 'JPN', GETDATE(), NULL, 0);

INSERT INTO country (id, [name], iso_alpha3_code, created_on, updated_on, is_disabled)
VALUES ('0d4d1993-9633-4f18-a7b8-4b0f24be18ef', 'Brazil', 'BRA', GETDATE(), null, 0);


-- DIRECTORS:
INSERT INTO director (id, country_id, [name], date_of_birth, created_on, updated_on, is_disabled)
VALUES ('c11bfa47-b6a9-471e-a797-b9189d78d3bd', '989adb5a-3434-4239-bfaa-8752dcd18e9b', 'Francis Ford Coppola', '1939-04-07', GETDATE(), NULL, 0);

INSERT INTO director (id, country_id, [name], date_of_birth, created_on, updated_on, is_disabled)
VALUES ('9e456246-54e9-48c0-9334-2c6eea386d6b', '90aa24a3-8cf4-48eb-8164-60351c748ebe', 'Hayao Miyazaki', '1941-01-05', GETDATE(), NULL, 0);

INSERT INTO director (id, country_id, [name], date_of_birth, created_on, updated_on, is_disabled)
VALUES ('c462cd8e-fc9f-444b-b540-6e6145b62de4', '0d4d1993-9633-4f18-a7b8-4b0f24be18ef', 'José Padilha', '1967-08-01', GETDATE(), null, 0);

INSERT INTO director (id, country_id, [name], date_of_birth, created_on, updated_on, is_disabled)
VALUES ('aa4318b4-9f2b-49da-a47a-6616f7b6c94a', '0d4d1993-9633-4f18-a7b8-4b0f24be18ef', 'Fernando Meirelles', '1955-11-09', GETDATE(), null, 0);

INSERT INTO director (id, country_id, [name], date_of_birth, created_on, updated_on, is_disabled)
VALUES ('c34a7a57-b11d-4f36-a4c9-e3807f34f101', '0d4d1993-9633-4f18-a7b8-4b0f24be18ef', 'Walter Sales', '1956-04-12', GETDATE(), null, 0);


-- MOVIES:
INSERT INTO movie (id, director_id, country_id, english_name, original_name, release_year, runtime_in_minutes, created_on, updated_on, is_disabled)
VALUES ('34478c13-e385-467b-a8bd-b127b1113720', 'c11bfa47-b6a9-471e-a797-b9189d78d3bd', '989adb5a-3434-4239-bfaa-8752dcd18e9b', 'The Godfather', NULL, '1972', 175, GETDATE(), NULL, 0);

INSERT INTO movie (id, director_id, country_id, english_name, original_name, release_year, runtime_in_minutes, created_on, updated_on, is_disabled)
VALUES ('9f27568d-9b6f-48e2-8bd4-f0aa9d9fead4', 'c11bfa47-b6a9-471e-a797-b9189d78d3bd', '989adb5a-3434-4239-bfaa-8752dcd18e9b', 'The Godfather Part II', NULL, '1974', 202, GETDATE(), NULL, 0);

INSERT INTO movie (id, director_id, country_id, english_name, original_name, release_year, runtime_in_minutes, created_on, updated_on, is_disabled)
VALUES ('86270dc9-e820-4c9c-8920-870028a93337', 'c11bfa47-b6a9-471e-a797-b9189d78d3bd', '989adb5a-3434-4239-bfaa-8752dcd18e9b', 'The Conversation', NULL, '1974', 114, GETDATE(), NULL, 0);

INSERT INTO movie (id, director_id, country_id, english_name, original_name, release_year, runtime_in_minutes, created_on, updated_on, is_disabled)
VALUES ('0015f5e0-aead-4017-99a3-5d189f184fd8', 'c11bfa47-b6a9-471e-a797-b9189d78d3bd', '989adb5a-3434-4239-bfaa-8752dcd18e9b', 'Apocalypse Now', NULL, '1979', 147, GETDATE(), NULL, 0);

INSERT INTO movie (id, director_id, country_id, english_name, original_name, release_year, runtime_in_minutes, created_on, updated_on, is_disabled)
VALUES ('d54465ac-f078-4131-829b-e16c8967dff1', 'c11bfa47-b6a9-471e-a797-b9189d78d3bd', '989adb5a-3434-4239-bfaa-8752dcd18e9b', 'The Godfather Part III', NULL, '1990', 162, GETDATE(), NULL, 0);

INSERT INTO movie (id, director_id, country_id, english_name, original_name, release_year, runtime_in_minutes, created_on, updated_on, is_disabled)
VALUES ('fabc749b-8eff-42c1-9b4e-f0980a8eb914', 'c11bfa47-b6a9-471e-a797-b9189d78d3bd', '989adb5a-3434-4239-bfaa-8752dcd18e9b', 'Bram Stoker''s Dracula', NULL, '1992', 128, GETDATE(), NULL, 0);

---

INSERT INTO movie (id, director_id, country_id, english_name, original_name, release_year, runtime_in_minutes, created_on, updated_on, is_disabled)
VALUES ('9edf0381-b758-4c52-a984-6be6d2361f37', '9e456246-54e9-48c0-9334-2c6eea386d6b', '90aa24a3-8cf4-48eb-8164-60351c748ebe', 'Nausicaä of the Valley of the Wind', N'風の谷のナウシカ', '1984', 117, GETDATE(), NULL, 0);

INSERT INTO movie (id, director_id, country_id, english_name, original_name, release_year, runtime_in_minutes, created_on, updated_on, is_disabled)
VALUES ('0717dd95-307d-438c-afa0-e8d1f19d1b30', '9e456246-54e9-48c0-9334-2c6eea386d6b', '90aa24a3-8cf4-48eb-8164-60351c748ebe', 'My Neighbor Totoro', N'となりのトトロ', '1988', 86, GETDATE(), NULL, 0);

INSERT INTO movie (id, director_id, country_id, english_name, original_name, release_year, runtime_in_minutes, created_on, updated_on, is_disabled)
VALUES ('8502369d-7554-4a20-8f8d-b3e9cda04573', '9e456246-54e9-48c0-9334-2c6eea386d6b', '90aa24a3-8cf4-48eb-8164-60351c748ebe', 'Princess Mononoke', N'もののけ姫', '1997', 134, GETDATE(), NULL, 0);

INSERT INTO movie (id, director_id, country_id, english_name, original_name, release_year, runtime_in_minutes, created_on, updated_on, is_disabled)
VALUES ('2197bc6c-c63f-4b15-97a9-d51facdea2bc', '9e456246-54e9-48c0-9334-2c6eea386d6b', '90aa24a3-8cf4-48eb-8164-60351c748ebe', 'Spirited Away', N'千と千尋の神隠し', '2001', 125, GETDATE(), NULL, 0);

INSERT INTO movie (id, director_id, country_id, english_name, original_name, release_year, runtime_in_minutes, created_on, updated_on, is_disabled)
VALUES ('f0ee4777-a56d-4b49-a2f1-da2a2f8f69b8', '9e456246-54e9-48c0-9334-2c6eea386d6b', '90aa24a3-8cf4-48eb-8164-60351c748ebe', 'Howl''s Moving Castle', N'ハウルの動く城', '2004', 119, GETDATE(), NULL, 0);

INSERT INTO movie (id, director_id, country_id, english_name, original_name, release_year, runtime_in_minutes, created_on, updated_on, is_disabled)
VALUES ('b9b1e1ab-de70-4a7d-b729-25dc24d2a1f2', '9e456246-54e9-48c0-9334-2c6eea386d6b', '90aa24a3-8cf4-48eb-8164-60351c748ebe', 'The Boy and the Heron', N'君たちはどう生きるか', '2023', 124, GETDATE(), NULL, 0);

---

INSERT INTO movie (id, director_id, country_id, english_name, original_name, release_year, runtime_in_minutes, created_on, updated_on, is_disabled)
VALUES ('2661fc29-b95c-40b1-bcb2-de57101c0890', 'c462cd8e-fc9f-444b-b540-6e6145b62de4', '0d4d1993-9633-4f18-a7b8-4b0f24be18ef', 'Elite Squad', 'Tropa de Elite', '2007', 115, GETDATE(), NULL, 0);

INSERT INTO movie (id, director_id, country_id, english_name, original_name, release_year, runtime_in_minutes, created_on, updated_on, is_disabled)
VALUES ('7f629faa-19be-41ef-8be6-f9b1e489ce77', 'c462cd8e-fc9f-444b-b540-6e6145b62de4', '0d4d1993-9633-4f18-a7b8-4b0f24be18ef', 'Elite Squad: The Enemy Within', 'Tropa de Elite: O Inimigo Agora é Outro', '2010', 115, GETDATE(), NULL, 0);

---

INSERT INTO movie (id, director_id, country_id, english_name, original_name, release_year, runtime_in_minutes, created_on, updated_on, is_disabled)
VALUES ('ded9f865-b447-4937-b827-ecb2328c1ad0', 'aa4318b4-9f2b-49da-a47a-6616f7b6c94a', '0d4d1993-9633-4f18-a7b8-4b0f24be18ef', 'City of God', 'Cidade de Deus', '2002', 129, GETDATE(), NULL, 0);

---

INSERT INTO movie (id, director_id, country_id, english_name, original_name, release_year, runtime_in_minutes, created_on, updated_on, is_disabled)
VALUES ('9dafbab3-b38d-40cd-8b23-2293861d7e2c', 'c34a7a57-b11d-4f36-a4c9-e3807f34f101', '0d4d1993-9633-4f18-a7b8-4b0f24be18ef', 'I''m Still Here', 'Ainda Estou Aqui', '2024', 129, GETDATE(), NULL, 0);


-- GENRES:
-- (all genre names were taken as reference from Letterboxd)
INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('54da1273-057a-4dc1-b7c7-05380dc3f371', 'Action', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('f6fce941-cb59-4ab9-b3ac-eb193a9d6bf0', 'Adventure', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('ec572c37-f9ab-406f-b41e-c31e9b971f08', 'Animation', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('aada9633-99ff-444d-bef8-e0c0f60e2e73', 'Comedy', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('83590de8-dc22-46ef-8dbd-59a3855fad54', 'Crime', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('9074e234-d47b-4a08-b656-2e020aed4544', 'Documentary', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('d558f793-6432-4585-882d-20394d95529c', 'Drama', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('d52a1e99-27a3-45b6-b2e8-054aea2065fd', 'Family', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('21547326-7b9f-4f6f-86d1-b0d7eaf9e78c', 'Fantasy', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('ace0ff40-e26d-4ea9-9e47-a01685b59aa5', 'History', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('f6bbcb0c-3216-4899-9d47-895f52ddd5d5', 'Horror', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('9f27c2ba-4e92-444a-aeda-f72c4829d3ed', 'Music', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('6b281cb2-218e-40fc-adb9-54c481a3654a', 'Mystery', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('56b03532-2af1-4ec5-9f75-a27730ee6f82', 'Romance', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('ccbd5c48-7de5-4292-8595-2ee0503c5519', 'Science Fiction', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('263162d3-a89a-4553-951d-bc000d286ee2', 'Thriller', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('56405b9a-44cb-4aff-87f5-53a5a653e56e', 'TV Movie', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('a7f7abf5-d34d-4958-ae8c-7616f6613ea8', 'War', GETDATE(), NULL, 0);

INSERT INTO genre (id, [name], created_on, updated_on, is_disabled)
VALUES ('c4b1f546-7300-4cfc-bf83-588268176ff8', 'Western', GETDATE(), NULL, 0);

-- Many-to-Many between MOVIE and GENRE:
-- The Godfather <> Crime
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('34478c13-e385-467b-a8bd-b127b1113720', '83590de8-dc22-46ef-8dbd-59a3855fad54');

-- The Godfather <> Drama
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('34478c13-e385-467b-a8bd-b127b1113720', 'd558f793-6432-4585-882d-20394d95529c');


-- The Godfather Part II <> Crime
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('9f27568d-9b6f-48e2-8bd4-f0aa9d9fead4', '83590de8-dc22-46ef-8dbd-59a3855fad54');

-- The Godfather Part II <> Drama
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('9f27568d-9b6f-48e2-8bd4-f0aa9d9fead4', 'd558f793-6432-4585-882d-20394d95529c');


-- The Conversation <> Drama
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('86270dc9-e820-4c9c-8920-870028a93337', 'd558f793-6432-4585-882d-20394d95529c');

-- The Conversation <> Crime
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('86270dc9-e820-4c9c-8920-870028a93337', '83590de8-dc22-46ef-8dbd-59a3855fad54');

-- The Conversation <> Mystery
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('86270dc9-e820-4c9c-8920-870028a93337', '6b281cb2-218e-40fc-adb9-54c481a3654a');


-- The Godfather Part III <> Crime
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('d54465ac-f078-4131-829b-e16c8967dff1', '83590de8-dc22-46ef-8dbd-59a3855fad54');

-- The Godfather Part III <> Drama
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('d54465ac-f078-4131-829b-e16c8967dff1', 'd558f793-6432-4585-882d-20394d95529c');

-- The Godfather Part III <> Thriller
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('d54465ac-f078-4131-829b-e16c8967dff1', '263162d3-a89a-4553-951d-bc000d286ee2');


-- Apocalypse Now <> Drama
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('0015f5e0-aead-4017-99a3-5d189f184fd8', 'd558f793-6432-4585-882d-20394d95529c');

-- Apocalypse Now <> War
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('0015f5e0-aead-4017-99a3-5d189f184fd8', 'a7f7abf5-d34d-4958-ae8c-7616f6613ea8');


-- Bram Stoker’s Dracula <> Horror
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('fabc749b-8eff-42c1-9b4e-f0980a8eb914', 'f6bbcb0c-3216-4899-9d47-895f52ddd5d5');

-- Bram Stoker’s Dracula <> Romance
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('fabc749b-8eff-42c1-9b4e-f0980a8eb914', '56b03532-2af1-4ec5-9f75-a27730ee6f82');

---

-- Nausicaä of the Valley of the Wind <> Adventure
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('9edf0381-b758-4c52-a984-6be6d2361f37', 'f6fce941-cb59-4ab9-b3ac-eb193a9d6bf0');

-- Nausicaä of the Valley of the Wind <> Animation
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('9edf0381-b758-4c52-a984-6be6d2361f37', 'ec572c37-f9ab-406f-b41e-c31e9b971f08');

-- Nausicaä of the Valley of the Wind <> Fantasy
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('9edf0381-b758-4c52-a984-6be6d2361f37', '21547326-7b9f-4f6f-86d1-b0d7eaf9e78c');


-- My Neighbor Totoro <> Animation
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('0717dd95-307d-438c-afa0-e8d1f19d1b30', 'ec572c37-f9ab-406f-b41e-c31e9b971f08');

-- My Neighbor Totoro <> Family
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('0717dd95-307d-438c-afa0-e8d1f19d1b30', 'd52a1e99-27a3-45b6-b2e8-054aea2065fd');

-- My Neighbor Totoro <> Fantasy
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('0717dd95-307d-438c-afa0-e8d1f19d1b30', '21547326-7b9f-4f6f-86d1-b0d7eaf9e78c');


-- Princess Mononoke <> Animation
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('8502369d-7554-4a20-8f8d-b3e9cda04573', 'ec572c37-f9ab-406f-b41e-c31e9b971f08');

-- Princess Mononoke <> Family
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('8502369d-7554-4a20-8f8d-b3e9cda04573', 'd52a1e99-27a3-45b6-b2e8-054aea2065fd');

-- Princess Mononoke <> Fantasy
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('8502369d-7554-4a20-8f8d-b3e9cda04573', '21547326-7b9f-4f6f-86d1-b0d7eaf9e78c');


-- Howl's Moving Castle <> Adventure
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('f0ee4777-a56d-4b49-a2f1-da2a2f8f69b8', 'f6fce941-cb59-4ab9-b3ac-eb193a9d6bf0');

-- Howl's Moving Castle <> Animation
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('f0ee4777-a56d-4b49-a2f1-da2a2f8f69b8', 'ec572c37-f9ab-406f-b41e-c31e9b971f08');

-- Howl's Moving Castle <> Fantasy
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('f0ee4777-a56d-4b49-a2f1-da2a2f8f69b8', '21547326-7b9f-4f6f-86d1-b0d7eaf9e78c');


-- Spirited Away <> Animation
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('2197bc6c-c63f-4b15-97a9-d51facdea2bc', 'ec572c37-f9ab-406f-b41e-c31e9b971f08');

-- Spirited Away <> Family
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('2197bc6c-c63f-4b15-97a9-d51facdea2bc', 'd52a1e99-27a3-45b6-b2e8-054aea2065fd');

-- Spirited Away <> Fantasy
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('2197bc6c-c63f-4b15-97a9-d51facdea2bc', '21547326-7b9f-4f6f-86d1-b0d7eaf9e78c');


-- The Boy and the Heron <> Adventure
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('b9b1e1ab-de70-4a7d-b729-25dc24d2a1f2', 'f6fce941-cb59-4ab9-b3ac-eb193a9d6bf0');

-- The Boy and the Heron <> Animation
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('b9b1e1ab-de70-4a7d-b729-25dc24d2a1f2', 'ec572c37-f9ab-406f-b41e-c31e9b971f08');

-- The Boy and the Heron <> Drama
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('b9b1e1ab-de70-4a7d-b729-25dc24d2a1f2', 'd558f793-6432-4585-882d-20394d95529c');

-- The Boy and the Heron <> Fantasy
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('b9b1e1ab-de70-4a7d-b729-25dc24d2a1f2', '21547326-7b9f-4f6f-86d1-b0d7eaf9e78c');

-- The Boy and the Heron <> Family
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('b9b1e1ab-de70-4a7d-b729-25dc24d2a1f2', 'd52a1e99-27a3-45b6-b2e8-054aea2065fd');

---

-- Elite Squad <> Action
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('2661fc29-b95c-40b1-bcb2-de57101c0890', '54da1273-057a-4dc1-b7c7-05380dc3f371');

-- Elite Squad <> Crime
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('2661fc29-b95c-40b1-bcb2-de57101c0890', '83590de8-dc22-46ef-8dbd-59a3855fad54');

-- Elite Squad <> Drama
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('2661fc29-b95c-40b1-bcb2-de57101c0890', 'd558f793-6432-4585-882d-20394d95529c');


-- Elite Squad: The Enemy Within <> Action
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('7f629faa-19be-41ef-8be6-f9b1e489ce77', '54da1273-057a-4dc1-b7c7-05380dc3f371');

-- Elite Squad: The Enemy Within <> Crime
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('7f629faa-19be-41ef-8be6-f9b1e489ce77', '83590de8-dc22-46ef-8dbd-59a3855fad54');

-- Elite Squad: The Enemy Within <> Drama
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('7f629faa-19be-41ef-8be6-f9b1e489ce77', 'd558f793-6432-4585-882d-20394d95529c');

---

-- City of God <> Crime
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('ded9f865-b447-4937-b827-ecb2328c1ad0', '83590de8-dc22-46ef-8dbd-59a3855fad54');

-- City of God <> Drama
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('ded9f865-b447-4937-b827-ecb2328c1ad0', 'd558f793-6432-4585-882d-20394d95529c');

---

-- I'm Still Here <> Drama
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('9dafbab3-b38d-40cd-8b23-2293861d7e2c', 'd558f793-6432-4585-882d-20394d95529c');

-- I'm Still Here <> History
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('9dafbab3-b38d-40cd-8b23-2293861d7e2c', 'ace0ff40-e26d-4ea9-9e47-a01685b59aa5');