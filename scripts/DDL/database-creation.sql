CREATE DATABASE Cinematica;

USE Cinematica;

CREATE TABLE [user] (
    id UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_user PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    [password] CHAR(32) NOT NULL,
    password_salt CHAR(24) NOT NULL,
    [role] VARCHAR(5) NOT NULL,
    created_on DATETIME2 NOT NULL,
    updated_on DATETIME2 NULL,
    is_disabled BIT NOT NULL
);

CREATE UNIQUE INDEX idx_unique_user_username
ON [user](username);

---

CREATE TABLE country (
    id UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_country PRIMARY KEY,
    [name] VARCHAR(255) UNIQUE,
    iso_alpha3_code VARCHAR(4) UNIQUE NOT NULL,
    created_on DATETIME2 NOT NULL,
    updated_on DATETIME2 NULL,
    is_disabled BIT NOT NULL
);

---

CREATE TABLE director (
    id UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_director PRIMARY KEY,
    country_id UNIQUEIDENTIFIER NOT NULL,
    [name] VARCHAR(255) UNIQUE NOT NULL,
    date_of_birth DATE NOT NULL,
    created_on DATETIME2 NOT NULL,
    updated_on DATETIME2 NULL,
    is_disabled BIT NOT NULL,

    CONSTRAINT FK_country_director
        FOREIGN KEY (country_id)
            REFERENCES country(id)
);

---

CREATE TABLE film (
    id UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_film PRIMARY KEY,
    director_id UNIQUEIDENTIFIER NOT NULL,
    country_id UNIQUEIDENTIFIER NOT NULL,
    [name] VARCHAR(255) NOT NULL,
    original_name NVARCHAR(255) NULL,
    release_year CHAR(4) NOT NULL,
    runtime_in_minutes SMALLINT NOT NULL,
    synopsis VARCHAR(500) NOT NULL,
    created_on DATETIME2 NOT NULL,
    updated_on DATETIME2 NULL,
    is_disabled BIT NOT NULL,

    CONSTRAINT FK_director_film
        FOREIGN KEY (director_id)
            REFERENCES director(id),

    CONSTRAINT FK_country_film
        FOREIGN KEY (country_id)
            REFERENCES country(id)
);

CREATE INDEX idx_film_name
ON [film]([name]);

---

CREATE TABLE genre (
    id UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_genre PRIMARY KEY,
    [name] VARCHAR(50) UNIQUE NOT NULL,
    created_on DATETIME2 NOT NULL,
    updated_on DATETIME2 NULL,
    is_disabled BIT NOT NULL
);

---

-- Junction table for many-to-many relationship between "film" and "genre" tables
CREATE TABLE film_genre (
    film_id UNIQUEIDENTIFIER NOT NULL,
    genre_id UNIQUEIDENTIFIER NOT NULL,

    CONSTRAINT PK_film_genre
        PRIMARY KEY (film_id, genre_id),

    CONSTRAINT FK_film_film_genre
        FOREIGN KEY (film_id)
            REFERENCES film(id),

    CONSTRAINT FK_genre_film_genre
        FOREIGN KEY (genre_id)
            REFERENCES genre(id)
);