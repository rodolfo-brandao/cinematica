CREATE DATABASE MovieLibrary;

USE MovieLibrary;

CREATE TABLE [user] (
    id UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_user PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    [password] CHAR(32) NOT NULL,
    password_salt CHAR(24) NOT NULL,
    [role] VARCHAR(5) NOT NULL,
    created_on DATETIME2 NOT NULL,
    updated_on DATETIME2 NULL,
    is_disabled BIT NOT NULL
);

CREATE TABLE country (
    id UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_country PRIMARY KEY,
    [name] VARCHAR(255) UNIQUE,
    iso_alpha3_code VARCHAR(4) UNIQUE NOT NULL,
    created_on DATETIME2 NOT NULL,
    updated_on DATETIME2 NULL,
    is_disabled BIT NOT NULL
);

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

CREATE TABLE movie (
    id UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_movie PRIMARY KEY,
    director_id UNIQUEIDENTIFIER NOT NULL,
    country_id UNIQUEIDENTIFIER NOT NULL,
    english_name VARCHAR(255) NOT NULL,
    original_name NVARCHAR(255) NULL,
    release_year CHAR(4) NOT NULL,
    runtime_in_minutes SMALLINT NOT NULL,
    created_on DATETIME2 NOT NULL,
    updated_on DATETIME2 NULL,
    is_disabled BIT NOT NULL,

    CONSTRAINT FK_director_movie
        FOREIGN KEY (director_id)
            REFERENCES director(id),

    CONSTRAINT FK_country_movie
        FOREIGN KEY (country_id)
            REFERENCES country(id)
);

CREATE TABLE genre (
    id UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_genre PRIMARY KEY,
    [name] VARCHAR(50) NOT NULL,
    created_on DATETIME2 NOT NULL,
    updated_on DATETIME2 NULL,
    is_disabled BIT NOT NULL
);

-- Junction table for many-to-many relationship between "movie" and "genre"
CREATE TABLE movie_genre (
    movie_id UNIQUEIDENTIFIER NOT NULL,
    genre_id UNIQUEIDENTIFIER NOT NULL,

    CONSTRAINT PK_movie_genre
        PRIMARY KEY (movie_id, genre_id),

    CONSTRAINT FK_movie_movie_genre
        FOREIGN KEY (movie_id)
            REFERENCES movie(id),

    CONSTRAINT FK_genre_movie_genre
        FOREIGN KEY (genre_id)
            REFERENCES genre(id)
);