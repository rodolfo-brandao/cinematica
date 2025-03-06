using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Cinematica.Core.Models;

namespace Cinematica.Data.EntityTypeConfigurations;

public class MovieEntityTypeConfiguration : IEntityTypeConfiguration<Movie>
{
    public void Configure(EntityTypeBuilder<Movie> builder)
    {
        builder.ToTable("movie");

        builder.HasKey(movie => movie.Id);

        builder.Property(movie => movie.Id)
            .HasColumnName("id")
            .HasColumnType("UNIQUEIDENTIFIER")
            .IsRequired();

        builder.Property(movie => movie.DirectorId)
            .HasColumnName("director_id")
            .HasColumnType("UNIQUEIDENTIFIER")
            .IsRequired();

        builder.Property(movie => movie.CountryId)
            .HasColumnName("country_id")
            .HasColumnType("UNIQUEIDENTIFIER")
            .IsRequired();

        builder.Property(movie => movie.Name)
            .HasColumnName("name")
            .HasColumnType("VARCHAR(255)")
            .IsRequired();

        builder.Property(movie => movie.OriginalName)
            .HasColumnName("original_name")
            .HasColumnType("NVARCHAR(255)")
            .IsRequired(required: false);

        builder.Property(movie => movie.ReleaseYear)
            .HasColumnName("release_year")
            .HasColumnType("CHAR(4)")
            .IsRequired();

        builder.Property(movie => movie.RuntimeInMinutes)
            .HasColumnName("runtime_in_minutes")
            .HasColumnType("SMALLINT")
            .IsRequired();
        
        builder.Property(movie => movie.Synopsis)
            .HasColumnName("synopsis")
            .HasColumnType("VARCHAR(500)")
            .IsRequired();

        builder.Property(movie => movie.CreatedOn)
            .HasColumnName("created_on")
            .HasColumnType("DATETIME2")
            .IsRequired();

        builder.Property(movie => movie.UpdatedOn)
            .HasColumnName("updated_on")
            .HasColumnType("DATETIME2")
            .IsRequired(required: false);

        builder.Property(movie => movie.IsDisabled)
            .HasColumnName("is_disabled")
            .HasColumnType("BIT")
            .IsRequired();

        #region Navigation Properties Cardinality

        builder.HasOne(movie => movie.Director)
            .WithMany(director => director.Movies)
            .HasForeignKey(movie => movie.DirectorId)
            .HasConstraintName("FK_director_movie")
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasOne(movie => movie.Country)
            .WithMany(country => country.Movies)
            .HasForeignKey(movie => movie.CountryId)
            .HasConstraintName("FK_country_movie")
            .OnDelete(DeleteBehavior.Restrict);

        #endregion
    }
}