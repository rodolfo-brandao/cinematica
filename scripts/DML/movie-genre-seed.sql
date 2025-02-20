-- Junction table to represent the many-to-many relationship between "Movie" and "Genre" tables.

USE MovieLibrary;

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

---

-- The Wages of Fear <> Adventure
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('2b22343e-b122-4b46-bd68-d0bad2a0a309', 'f6fce941-cb59-4ab9-b3ac-eb193a9d6bf0');

-- The Wages of Fear <> Drama
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('2b22343e-b122-4b46-bd68-d0bad2a0a309', 'd558f793-6432-4585-882d-20394d95529c');

-- The Wages of Fear <> Thriller
INSERT INTO movie_genre (movie_id, genre_id)
VALUES ('2b22343e-b122-4b46-bd68-d0bad2a0a309', '263162d3-a89a-4553-951d-bc000d286ee2');