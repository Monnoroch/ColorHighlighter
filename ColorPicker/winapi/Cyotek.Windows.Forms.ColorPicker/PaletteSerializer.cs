using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;

namespace Cyotek.Windows.Forms
{
  // Cyotek Color Picker controls library
  // Copyright © 2013-2015 Cyotek Ltd.
  // http://cyotek.com/blog/tag/colorpicker

  // Licensed under the MIT License. See license.txt for the full text.

  // If you use this code in your applications, donations or attribution are welcome

  /// <summary>
  /// Serializes and deserializes color palettes into and from other documents.
  /// </summary>
  public abstract class PaletteSerializer : IPaletteSerializer
  {
    #region Constants

    private static string _defaultOpenFilter;

    private static string _defaultSaveFileter;

    private static readonly List<IPaletteSerializer> _serializerCache;

    #endregion

    #region Static Constructors

    /// <summary>
    /// Initializes static members of the <see cref="PaletteSerializer"/> class.
    /// </summary>
    static PaletteSerializer()
    {
      _serializerCache = new List<IPaletteSerializer>();
    }

    #endregion

    #region Public Class Properties

    /// <summary>
    /// Gets all loaded serializers.
    /// </summary>
    /// <value>The loaded serializers.</value>
    public static IEnumerable<IPaletteSerializer> AllSerializers
    {
      get { return _serializerCache.AsReadOnly(); }
    }

    /// <summary>
    /// Returns a filter suitable for use with the <see cref="System.Windows.Forms.OpenFileDialog"/>.
    /// </summary>
    /// <value>A filter suitable for use with the <see cref="System.Windows.Forms.OpenFileDialog"/>.</value>
    /// <remarks>This filter does not include any serializers that cannot read source data.</remarks>
    public static string DefaultOpenFilter
    {
      get
      {
        if (string.IsNullOrEmpty(_defaultOpenFilter))
        {
          CreateFilters();
        }

        return _defaultOpenFilter;
      }
    }

    /// <summary>
    /// Returns a filter suitable for use with the <see cref="System.Windows.Forms.SaveFileDialog"/>.
    /// </summary>
    /// <value>A filter suitable for use with the <see cref="System.Windows.Forms.SaveFileDialog"/>.</value>
    /// <remarks>This filter does not include any serializers that cannot write destination data.</remarks>
    public static string DefaultSaveFilter
    {
      get
      {
        if (string.IsNullOrEmpty(_defaultSaveFileter))
        {
          CreateFilters();
        }

        return _defaultSaveFileter;
      }
    }

    #endregion

    #region Public Class Members

    public static IPaletteSerializer GetSerializer(string fileName)
    {
      IPaletteSerializer result;

      if (string.IsNullOrEmpty(fileName))
      {
        throw new ArgumentNullException("fileName");
      }

      if (!File.Exists(fileName))
      {
        throw new FileNotFoundException(string.Format("Cannot find file '{0}'.", fileName), fileName);
      }

      if (_serializerCache.Count == 0)
      {
        LoadSerializers();
      }

      result = null;

      foreach (IPaletteSerializer checkSerializer in AllSerializers)
      {
        using (FileStream file = File.OpenRead(fileName))
        {
          if (checkSerializer.CanReadFrom(file))
          {
            result = checkSerializer;
            break;
          }
        }
      }

      return result;
    }

    #endregion

    #region Private Class Members

    /// <summary>
    /// Creates the Open and Save As filters.
    /// </summary>
    private static void CreateFilters()
    {
      StringBuilder openFilter;
      StringBuilder saveFilter;
      List<string> openExtensions;

      openExtensions = new List<string>();
      openFilter = new StringBuilder();
      saveFilter = new StringBuilder();

      if (_serializerCache.Count == 0)
      {
        LoadSerializers();
      }

      foreach (IPaletteSerializer serializer in _serializerCache.Where(serializer => !(string.IsNullOrEmpty(serializer.DefaultExtension) || openExtensions.Contains(serializer.DefaultExtension))))
      {
        StringBuilder extensionMask;
        string filter;

        extensionMask = new StringBuilder();

        foreach (string extension in serializer.DefaultExtension.Split(new[]
                                                                       {
                                                                         ';'
                                                                       }, StringSplitOptions.RemoveEmptyEntries))
        {
          string mask;

          mask = "*." + extension;

          if (!openExtensions.Contains(mask))
          {
            openExtensions.Add(mask);
          }

          if (extensionMask.Length != 0)
          {
            extensionMask.Append(";");
          }
          extensionMask.Append(mask);
        }

        filter = string.Format("{0} Files ({1})|{1}", serializer.Name, extensionMask);

        if (serializer.CanRead)
        {
          if (openFilter.Length != 0)
          {
            openFilter.Append("|");
          }
          openFilter.Append(filter);
        }

        if (serializer.CanWrite)
        {
          if (saveFilter.Length != 0)
          {
            saveFilter.Append("|");
          }
          saveFilter.Append(filter);
        }
      }

      if (openExtensions.Count != 0)
      {
        openFilter.Insert(0, string.Format("All Supported Palettes ({0})|{0}|", string.Join(";", openExtensions.ToArray())));
      }
      if (openFilter.Length != 0)
      {
        openFilter.Append("|");
      }
      openFilter.Append("All Files (*.*)|*.*");

      _defaultOpenFilter = openFilter.ToString();
      _defaultSaveFileter = saveFilter.ToString();
    }

    /// <summary>
    /// Gets the loadable types from an assembly.
    /// </summary>
    /// <param name="assembly">The assembly to load types from.</param>
    /// <returns>Available types</returns>
    private static IEnumerable<Type> GetLoadableTypes(Assembly assembly)
    {
      try
      {
        return assembly.GetTypes();
      }
      catch (ReflectionTypeLoadException ex)
      {
        return ex.Types.Where(x => x != null);
      }
    }

    /// <summary>
    /// Loads the serializers.
    /// </summary>
    private static void LoadSerializers()
    {
      _serializerCache.Clear();
      _defaultOpenFilter = null;
      _defaultSaveFileter = null;

      foreach (Type type in AppDomain.CurrentDomain.GetAssemblies().SelectMany(assembly => GetLoadableTypes(assembly).Where(type => !type.IsAbstract && type.IsPublic && typeof(IPaletteSerializer).IsAssignableFrom(type))))
      {
        try
        {
          _serializerCache.Add((IPaletteSerializer)Activator.CreateInstance(type));
        }
          // ReSharper disable EmptyGeneralCatchClause
        catch
          // ReSharper restore EmptyGeneralCatchClause
        {
          // ignore errors
        }
      }

      // sort the cache by name, that way the open/save filters won't need independant sorting
      // and can easily map FileDialog.FilterIndex to an item in this collection
      _serializerCache.Sort((a, b) => String.CompareOrdinal(a.Name, b.Name));
    }

    #endregion

    #region Public Properties

    /// <summary>
    /// Gets a value indicating whether this serializer can be used to read palettes.
    /// </summary>
    /// <value><c>true</c> if palettes can be read using this serializer; otherwise, <c>false</c>.</value>
    [Browsable(false)]
    public virtual bool CanRead
    {
      get { return true; }
    }

    /// <summary>
    /// Gets a value indicating whether this serializer can be used to write palettes.
    /// </summary>
    /// <value><c>true</c> if palettes can be written using this serializer; otherwise, <c>false</c>.</value>
    [Browsable(false)]
    public virtual bool CanWrite
    {
      get { return true; }
    }

    /// <summary>
    /// Gets the default extension for files generated with this palette format.
    /// </summary>
    /// <value>The default extension for files generated with this palette format.</value>
    [Browsable(false)]
    public abstract string DefaultExtension { get; }

    /// <summary>
    /// Gets a descriptive name of the palette format
    /// </summary>
    /// <value>The descriptive name of the palette format.</value>
    [Browsable(false)]
    public abstract string Name { get; }

    #endregion

    #region Public Members

    /// <summary>
    /// Determines whether this instance can read palette from data the specified stream.
    /// </summary>
    /// <param name="stream">The stream.</param>
    /// <returns><c>true</c> if this instance can read palette data from the specified stream; otherwise, <c>false</c>.</returns>
    public abstract bool CanReadFrom(Stream stream);

    /// <summary>
    /// Deserializes the <see cref="ColorCollection" /> contained by the specified <see cref="Stream" />.
    /// </summary>
    /// <param name="stream">The <see cref="Stream" /> that contains the palette to deserialize.</param>
    /// <returns>The <see cref="ColorCollection" /> being deserialized.</returns>
    public abstract ColorCollection Deserialize(Stream stream);

    /// <summary>
    /// Deserializes the <see cref="ColorCollection" /> contained by the specified <see cref="Stream" />.
    /// </summary>
    /// <param name="fileName">The name of the file that the palette will be read from.</param>
    /// <returns>The <see cref="ColorCollection" /> being deserialized.</returns>
    public ColorCollection Deserialize(string fileName)
    {
      if (!File.Exists(fileName))
      {
        throw new FileNotFoundException(string.Format("Cannot find file '{0}'", fileName), fileName);
      }

      using (Stream stream = File.OpenRead(fileName))
      {
        return this.Deserialize(stream);
      }
    }

    /// <summary>
    /// Serializes the specified <see cref="ColorCollection" /> and writes the palette to a file using the specified <see cref="Stream"/>.
    /// </summary>
    /// <param name="stream">The <see cref="Stream" /> used to write the palette.</param>
    /// <param name="palette">The <see cref="ColorCollection" /> to serialize.</param>
    public abstract void Serialize(Stream stream, ColorCollection palette);

    /// <summary>
    /// Serializes the specified <see cref="ColorCollection" /> and writes the palette to a file using the specified <see cref="Stream"/>.
    /// </summary>
    /// <param name="fileName">The name of the file where the palette will be written to.</param>
    /// <param name="palette">The <see cref="ColorCollection" /> to serialize.</param>
    public void Serialize(string fileName, ColorCollection palette)
    {
      using (Stream stream = File.Create(fileName))
      {
        this.Serialize(stream, palette);
      }
    }

    #endregion

    #region Protected Members

    /// <summary>
    /// Reads a 16bit unsigned integer in big-endian format.
    /// </summary>
    /// <param name="stream">The stream to read the data from.</param>
    /// <returns>The unsigned 16bit integer cast to an <c>Int32</c>.</returns>
    protected int ReadInt16(Stream stream)
    {
      return (stream.ReadByte() << 8) | (stream.ReadByte() << 0);
    }

    /// <summary>
    /// Reads a 32bit unsigned integer in big-endian format.
    /// </summary>
    /// <param name="stream">The stream to read the data from.</param>
    /// <returns>The unsigned 32bit integer cast to an <c>Int32</c>.</returns>
    protected int ReadInt32(Stream stream)
    {
      // big endian conversion: http://stackoverflow.com/a/14401341/148962

      return ((byte)stream.ReadByte() << 24) | ((byte)stream.ReadByte() << 16) | ((byte)stream.ReadByte() << 8) | (byte)stream.ReadByte();
    }

    /// <summary>
    /// Reads a unicode string of the specified length.
    /// </summary>
    /// <param name="stream">The stream to read the data from.</param>
    /// <param name="length">The number of characters in the string.</param>
    /// <returns>The string read from the stream.</returns>
    protected string ReadString(Stream stream, int length)
    {
      byte[] buffer;

      buffer = new byte[length * 2];

      stream.Read(buffer, 0, buffer.Length);

      return Encoding.BigEndianUnicode.GetString(buffer);
    }

    /// <summary>
    /// Writes a 16bit unsigned integer in big-endian format.
    /// </summary>
    /// <param name="stream">The stream to write the data to.</param>
    /// <param name="value">The value to write</param>
    protected void WriteInt16(Stream stream, short value)
    {
      stream.WriteByte((byte)(value >> 8));
      stream.WriteByte((byte)(value >> 0));
    }

    /// <summary>
    /// Writes a 32bit unsigned integer in big-endian format.
    /// </summary>
    /// <param name="stream">The stream to write the data to.</param>
    /// <param name="value">The value to write</param>
    protected void WriteInt32(Stream stream, int value)
    {
      stream.WriteByte((byte)((value & 0xFF000000) >> 24));
      stream.WriteByte((byte)((value & 0x00FF0000) >> 16));
      stream.WriteByte((byte)((value & 0x0000FF00) >> 8));
      stream.WriteByte((byte)((value & 0x000000FF) >> 0));
    }

    protected void WriteString(Stream stream, string value)
    {
      stream.Write(Encoding.BigEndianUnicode.GetBytes(value), 0, value.Length * 2);
    }

    #endregion

    #region IPaletteSerializer Members

    /// <summary>
    /// Serializes the specified <see cref="ColorCollection" /> and writes the palette to a file using the specified Stream.
    /// </summary>
    /// <param name="stream">The <see cref="Stream" /> used to write the palette.</param>
    /// <param name="palette">The <see cref="ColorCollection" /> to serialize.</param>
    void IPaletteSerializer.Serialize(Stream stream, ColorCollection palette)
    {
      this.Serialize(stream, palette);
    }

    /// <summary>
    /// Deserializes the <see cref="ColorCollection" /> contained by the specified <see cref="Stream" />.
    /// </summary>
    /// <param name="stream">The <see cref="Stream" /> that contains the palette to deserialize.</param>
    /// <returns>The <see cref="ColorCollection" /> being deserialized.</returns>
    ColorCollection IPaletteSerializer.Deserialize(Stream stream)
    {
      return this.Deserialize(stream);
    }

    /// <summary>
    /// Gets a descriptive name of the palette format
    /// </summary>
    /// <value>The descriptive name of the palette format.</value>
    string IPaletteSerializer.Name
    {
      get { return this.Name; }
    }

    /// <summary>
    /// Gets the default extension for files generated with this palette format.
    /// </summary>
    /// <value>The default extension for files generated with this palette format.</value>
    string IPaletteSerializer.DefaultExtension
    {
      get { return this.DefaultExtension; }
    }

    /// <summary>
    /// Gets a value indicating whether this serializer can be used to read palettes.
    /// </summary>
    /// <value><c>true</c> if palettes can be read using this serializer; otherwise, <c>false</c>.</value>
    bool IPaletteSerializer.CanRead
    {
      get { return this.CanRead; }
    }

    /// <summary>
    /// Gets a value indicating whether this serializer can be used to write palettes.
    /// </summary>
    /// <value><c>true</c> if palettes can be written using this serializer; otherwise, <c>false</c>.</value>
    bool IPaletteSerializer.CanWrite
    {
      get { return this.CanWrite; }
    }

    /// <summary>
    /// Determines whether this instance can read palette data from the specified stream.
    /// </summary>
    /// <param name="stream">The stream.</param>
    /// <returns><c>true</c> if this instance can read palette data from the specified stream; otherwise, <c>false</c>.</returns>
    bool IPaletteSerializer.CanReadFrom(Stream stream)
    {
      return this.CanReadFrom(stream);
    }

    #endregion
  }
}
