using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Cinematica.Core.Models;

namespace Cinematica.Data.EntityTypeConfigurations;

public class FilmEntityTypeConfiguration : IEntityTypeConfiguration<Film>
{
    public void Configure(EntityTypeBuilder<Film> builder)
    {
        builder.ToTable("film");

        builder.HasKey(film => film.Id);

        builder.Property(film => film.Id)
            .HasColumnName("id")
            .HasColumnType("UNIQUEIDENTIFIER")
            .IsRequired();

        builder.Property(film => film.DirectorId)
            .HasColumnName("director_id")
            .HasColumnType("UNIQUEIDENTIFIER")
            .IsRequired();

        builder.Property(film => film.CountryId)
            .HasColumnName("country_id")
            .HasColumnType("UNIQUEIDENTIFIER")
            .IsRequired();

        builder.Property(film => film.Name)
            .HasColumnName("name")
            .HasColumnType("VARCHAR(255)")
            .IsRequired();

        builder.Property(film => film.OriginalName)
            .HasColumnName("original_name")
            .HasColumnType("NVARCHAR(255)")
            .IsRequired(required: false);

        builder.Property(film => film.ReleaseYear)
            .HasColumnName("release_year")
            .HasColumnType("CHAR(4)")
            .IsRequired();

        builder.Property(film => film.RuntimeInMinutes)
            .HasColumnName("runtime_in_minutes")
            .HasColumnType("SMALLINT")
            .IsRequired();
        
        builder.Property(film => film.Synopsis)
            .HasColumnName("synopsis")
            .HasColumnType("VARCHAR(500)")
            .IsRequired();

        builder.Property(film => film.CreatedOn)
            .HasColumnName("created_on")
            .HasColumnType("DATETIME2")
            .IsRequired();

        builder.Property(film => film.UpdatedOn)
            .HasColumnName("updated_on")
            .HasColumnType("DATETIME2")
            .IsRequired(required: false);

        builder.Property(film => film.IsDisabled)
            .HasColumnName("is_disabled")
            .HasColumnType("BIT")
            .IsRequired();

        #region Navigation Properties Cardinality

        builder.HasOne(film => film.Director)
            .WithMany(director => director.Films)
            .HasForeignKey(film => film.DirectorId)
            .HasConstraintName("FK_director_film")
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasOne(film => film.Country)
            .WithMany(country => country.Films)
            .HasForeignKey(film => film.CountryId)
            .HasConstraintName("FK_country_film")
            .OnDelete(DeleteBehavior.Restrict);

        #endregion
    }
}