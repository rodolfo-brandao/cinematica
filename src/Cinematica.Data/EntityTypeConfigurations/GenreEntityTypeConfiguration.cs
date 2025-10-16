using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Cinematica.Core.Models;

namespace Cinematica.Data.EntityTypeConfigurations;

public class GenreEntityTypeConfiguration : IEntityTypeConfiguration<Genre>
{
    public void Configure(EntityTypeBuilder<Genre> builder)
    {
        builder.ToTable("genre");
        
        builder.HasKey(genre => genre.Id);
        
        builder.Property(genre => genre.Id)
            .HasColumnName("id")
            .HasColumnType("UNIQUEIDENTIFIER")
            .IsRequired();
        
        builder.Property(genre => genre.Name)
            .HasColumnName("name")
            .HasColumnType("VARCHAR(50)")
            .IsRequired();
        
        builder.Property(genre => genre.CreatedAt)
            .HasColumnName("created_on")
            .HasColumnType("DATETIME2")
            .IsRequired();

        builder.Property(genre => genre.UpdatedAt)
            .HasColumnName("updated_on")
            .HasColumnType("DATETIME2")
            .IsRequired(required: false);

        builder.Property(genre => genre.IsDisabled)
            .HasColumnName("is_disabled")
            .HasColumnType("BIT")
            .IsRequired();
    }
}