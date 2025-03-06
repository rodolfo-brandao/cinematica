using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Cinematica.Core.Models;

namespace Cinematica.Data.EntityTypeConfigurations;

public class DirectorEntityTypeConfiguration : IEntityTypeConfiguration<Director>
{
    public void Configure(EntityTypeBuilder<Director> builder)
    {
        builder.ToTable("director");

        builder.HasKey(director => director.Id);

        builder.Property(director => director.Id)
            .HasColumnName("id")
            .HasColumnType("UNIQUEIDENTIFIER")
            .IsRequired();

        builder.Property(director => director.CountryId)
            .HasColumnName("country_id")
            .HasColumnType("UNIQUEIDENTIFIER")
            .IsRequired();

        builder.Property(director => director.Name)
            .HasColumnName("name")
            .HasColumnType("VARCHAR(50)")
            .IsRequired();

        builder.Property(director => director.DateOfBirth)
            .HasColumnName("date_of_birth")
            .HasColumnType("DATE")
            .IsRequired();

        builder.Property(director => director.CreatedOn)
            .HasColumnName("created_on")
            .HasColumnType("DATETIME2")
            .IsRequired();

        builder.Property(director => director.UpdatedOn)
            .HasColumnName("updated_on")
            .HasColumnType("DATETIME2")
            .IsRequired(required: false);

        builder.Property(director => director.IsDisabled)
            .HasColumnName("is_disabled")
            .HasColumnType("BIT")
            .IsRequired();

        #region Navigation Properties Cardinality

        builder.HasOne(director => director.Country)
            .WithMany(country => country.Directors)
            .HasForeignKey(director => director.CountryId)
            .HasConstraintName("FK_country_director")
            .OnDelete(DeleteBehavior.Restrict);

        #endregion
    }
}
