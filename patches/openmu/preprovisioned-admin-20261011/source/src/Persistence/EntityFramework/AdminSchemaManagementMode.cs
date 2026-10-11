// <copyright file="AdminSchemaManagementMode.cs" company="MUnique">
// Licensed under the MIT License. See LICENSE file in the project root for full license information.
// </copyright>

namespace MUnique.OpenMU.Persistence.EntityFramework;

using System.Xml.Serialization;

/// <summary>
/// Controls schema preparation by the admin user repository.
/// </summary>
[Serializable]
[XmlType(Namespace = "http://www.munique.net/ConnectionSettings")]
public enum AdminSchemaManagementMode
{
    /// <summary>
    /// The repository applies pending admin migrations, preserving the default behavior.
    /// </summary>
    RuntimeMigrations = 0,

    /// <summary>
    /// Setup provisions the schema separately. The repository only checks that the applied
    /// admin migration identifiers exactly match its compiled migrations and fails on errors.
    /// </summary>
    ExternallyProvisioned = 1,
}
