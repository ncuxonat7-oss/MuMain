// <copyright file="JsonBinaryProjectionTests.cs" company="MUnique">
// Licensed under the MIT License. See LICENSE file in the project root for full license information.
// </copyright>

namespace MUnique.OpenMU.Tests;

using System.IO;
using System.Text;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata;
using MUnique.OpenMU.Persistence.EntityFramework.CompiledModels.ForEntityDataContext;
using MUnique.OpenMU.Persistence.EntityFramework.Json;
using MUnique.OpenMU.Persistence.Json;
using GameMapDefinition = MUnique.OpenMU.Persistence.EntityFramework.Model.GameMapDefinition;
using GameConfiguration = MUnique.OpenMU.Persistence.EntityFramework.Model.GameConfiguration;

/// <summary>
/// Tests binary columns in PostgreSQL JSON projections without opening a database connection.
/// </summary>
[TestFixture]
public class JsonBinaryProjectionTests
{
    /// <summary>
    /// A binary table projects every mapped column exactly once, including shadow columns.
    /// </summary>
    [Test]
    public void MapColumnsAreProjectedOnce()
    {
        var model = EntityDataContextModel.Instance;
        var entityType = model.FindEntityType(typeof(GameMapDefinition))!;
        var query = new ScalarQueryBuilder().BuildJsonQueryForEntity(entityType);
        var table = model.GetRelationalModel().FindTable("GameMapDefinition", "config")!;
        var expectedColumns = table.Columns.OrderBy(column => column.Name, StringComparer.Ordinal)
            .Select(column => column.StoreType == "bytea"
                ? $"encode(a.\"{column.Name}\", 'base64') as \"{column.Name}\""
                : $"a.\"{column.Name}\"");
        var expected = "select a.\"Id\" as \"$id\", " + string.Join(", ", expectedColumns) + " from config.\"GameMapDefinition\" a";

        Assert.That(query, Does.Contain(expected));
        Assert.That(query, Does.Not.Contain("a.*"));
        Assert.That(query.Split("encode(").Length - 1, Is.EqualTo(1));
        Assert.That(query, Does.Contain("a.\"GameConfigurationId\""));
        Assert.That(query, Does.Contain("a.\"Discriminator\""));
    }

    /// <summary>
    /// Binary-free tables retain the original projection verbatim.
    /// </summary>
    [Test]
    public void BinaryFreeProjectionIsUnchanged()
    {
        var entityType = EntityDataContextModel.Instance.FindEntityType(typeof(GameConfiguration))!;
        var query = new ScalarQueryBuilder().BuildJsonQueryForEntity(entityType);
        var expected = "select result.\"Id\" \"$id\", result.\"Id\" id, row_to_json(result) as GameConfiguration" + Environment.NewLine
            + "from (" + Environment.NewLine
            + "select a.\"Id\" as \"$id\", a.* from config.\"GameConfiguration\" a" + Environment.NewLine
            + ") result" + Environment.NewLine;

        Assert.That(query, Is.EqualTo(expected));
    }

    /// <summary>
    /// The real aggregate query encodes nested map terrain and retains navigation projections.
    /// </summary>
    [Test]
    public void AggregateQueryEncodesNestedMaps()
    {
        var entityType = EntityDataContextModel.Instance.FindEntityType(typeof(GameConfiguration))!;
        var query = new GameConfigurationJsonQueryBuilder().BuildJsonQueryForEntity(entityType);

        Assert.That(query, Does.Contain("encode(b.\"TerrainData\", 'base64') as \"TerrainData\""));
        Assert.That(query, Does.Contain(") as \"RawMaps\""));
        Assert.That(query, Does.Contain("json_build_object('$ref', "));
        Assert.That(query, Does.Contain("coalesce(array_to_json(array_agg(row_to_json("));
        Assert.That(query, Does.Contain("select a.\"Id\" as \"$id\", a.*"));
    }

    /// <summary>
    /// Column metadata handles renamed binary fields, multiple binary columns and TPH columns.
    /// </summary>
    [Test]
    public void RenamedAndInheritedColumnsAreProjectedOnce()
    {
        using var context = new ProjectionContext();
        var entityType = context.Model.FindEntityType(typeof(BinaryEntity))!;
        var query = new ScalarQueryBuilder().BuildJsonQueryForEntity(entityType);

        Assert.That(query, Does.Contain("encode(a.\"Stored\"\"Payload\", 'base64') as \"Stored\"\"Payload\""));
        Assert.That(query, Does.Contain("encode(a.\"OtherPayload\", 'base64') as \"OtherPayload\""));
        Assert.That(query, Does.Contain("a.\"DerivedValue\""));
        Assert.That(query, Does.Contain("a.\"Discriminator\""));
        Assert.That(query, Does.Contain("a.\"ShadowValue\""));
        Assert.That(query, Does.Not.Contain("a.*"));
        Assert.That(query.Split("encode(").Length - 1, Is.EqualTo(2));
        Assert.That(query.Split("a.\"Stored\"\"Payload\"").Length - 1, Is.EqualTo(1));
        Assert.That(query.Split("a.\"OtherPayload\"").Length - 1, Is.EqualTo(1));
    }

    /// <summary>
    /// The actual generated map converter accepts null, empty, mixed and long base64 strings.
    /// PostgreSQL inserts line feeds after 76 base64 characters, which must remain accepted.
    /// </summary>
    /// <param name="length">The binary length, or -1 for null.</param>
    [TestCase(-1)]
    [TestCase(0)]
    [TestCase(4)]
    [TestCase(65536)]
    public void MapConverterAcceptsBase64(int length)
    {
        var bytes = length < 0 ? null : Enumerable.Range(0, length).Select(index => (byte)(index % 256)).ToArray();
        var encoded = bytes is null ? null : Convert.ToBase64String(bytes);
        if (encoded is { Length: > 76 })
        {
            encoded = string.Join("\n", Enumerable.Range(0, (encoded.Length + 75) / 76)
                .Select(index => encoded.Substring(index * 76, Math.Min(76, encoded.Length - (index * 76)))));
        }

        var id = Guid.NewGuid();
        var json = "{\"$id\":\"" + id + "\",\"Id\":\"" + id + "\",\"TerrainData\":" + JsonSerializer.Serialize(encoded) + "}";
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(json));
        var result = stream.FromJson<GameMapDefinition>();

        Assert.That(result, Is.Not.Null);
        Assert.That(result!.TerrainData, Is.EqualTo(bytes));
    }

    /// <summary>
    /// The original PostgreSQL hex representation reproduces the converter failure.
    /// </summary>
    [Test]
    public void MapConverterRejectsPostgresHex()
    {
        var id = Guid.NewGuid();
        var json = "{\"$id\":\"" + id + "\",\"Id\":\"" + id + "\",\"TerrainData\":\"\\\\x00ff107f\"}";
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(json));

        var exception = Assert.Throws<JsonException>(() => stream.FromJson<GameMapDefinition>());
        Assert.That(exception!.InnerException, Is.TypeOf<FormatException>());
    }

    private sealed class ScalarQueryBuilder : JsonQueryBuilder
    {
        protected override IEnumerable<INavigation> GetNavigations(IEntityType entityType) => [];
    }

    private sealed class ProjectionContext : DbContext
    {
        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            optionsBuilder.UseNpgsql();
        }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            var entity = modelBuilder.Entity<BinaryEntity>();
            entity.ToTable("BinaryEntity", "config");
            entity.Property(item => item.Payload).HasColumnName("Stored\"Payload");
            entity.Property<int>("ShadowValue");
            modelBuilder.Entity<DerivedBinaryEntity>();
        }
    }

    private class BinaryEntity
    {
        public Guid Id { get; set; }

        public byte[]? Payload { get; set; }

        public byte[]? OtherPayload { get; set; }
    }

    private sealed class DerivedBinaryEntity : BinaryEntity
    {
        public string? DerivedValue { get; set; }
    }
}
