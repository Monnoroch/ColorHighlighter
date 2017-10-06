using System;
using System.Drawing;
using System.IO;
using System.Text;

namespace Cyotek.Windows.Forms
{
  // Cyotek Color Picker controls library
  // Copyright © 2013-2015 Cyotek Ltd.
  // http://cyotek.com/blog/tag/colorpicker

  // Licensed under the MIT License. See license.txt for the full text.

  // If you use this code in your applications, donations or attribution are welcome

  // http://cyotek.com/blog/loading-the-color-palette-from-a-bbm-lbm-image-file-using-csharp

  /// <summary>
  /// Deserializes color palettes into and from the images and palettes using the  ILBM (IFF Interleaved Bitmap) format.
  /// </summary>
  public class InterleavedBitmapPaletteSerializer : PaletteSerializer
  {
    #region Overridden Properties

    /// <summary>
    /// Gets a value indicating whether this serializer can be used to write palettes.
    /// </summary>
    /// <value><c>true</c> if palettes can be written using this serializer; otherwise, <c>false</c>.</value>
    public override bool CanWrite
    {
      get { return false; }
    }

    /// <summary>
    /// Gets the default extension for files generated with this palette format.
    /// </summary>
    /// <value>The default extension for files generated with this palette format.</value>
    public override string DefaultExtension
    {
      get { return "bbm;lbm"; }
    }

    /// <summary>
    /// Gets a descriptive name of the palette format
    /// </summary>
    /// <value>The descriptive name of the palette format.</value>
    public override string Name
    {
      get { return "Interleaved Bitmap Palette"; }
    }

    #endregion

    #region Overridden Methods

    /// <summary>
    /// Determines whether this instance can read palette from data the specified stream.
    /// </summary>
    /// <param name="stream">The stream.</param>
    /// <returns><c>true</c> if this instance can read palette data from the specified stream; otherwise, <c>false</c>.</returns>
    public override bool CanReadFrom(Stream stream)
    {
      bool result;

      if (stream == null)
      {
        throw new ArgumentNullException("stream");
      }

      try
      {
        byte[] formHeaderData;
        byte[] imageHeaderData;
        string formHeader;
        string imageHeader;

        formHeaderData = new byte[4];
        imageHeaderData = new byte[4];

        stream.Read(formHeaderData, 0, formHeaderData.Length);
        this.ReadInt32(stream);
        stream.Read(imageHeaderData, 0, imageHeaderData.Length);

        formHeader = Encoding.ASCII.GetString(formHeaderData);
        imageHeader = Encoding.ASCII.GetString(imageHeaderData);

        result = formHeader == "FORM" && (imageHeader == "PBM " || imageHeader == "ILBM");
      }
      catch
      {
        result = false;
      }

      return result;
    }

    /// <summary>
    /// Deserializes the <see cref="ColorCollection" /> contained by the specified <see cref="Stream" />.
    /// </summary>
    /// <param name="stream">The <see cref="Stream" /> that contains the palette to deserialize.</param>
    /// <returns>The <see cref="ColorCollection" /> being deserialized.</returns>
    public override ColorCollection Deserialize(Stream stream)
    {
      byte[] buffer;
      string header;
      ColorCollection results;

      if (stream == null)
      {
        throw new ArgumentNullException("stream");
      }

      results = new ColorCollection();

      // read the FORM header that identifies the document as an IFF file
      buffer = new byte[4];
      stream.Read(buffer, 0, buffer.Length);
      if (Encoding.ASCII.GetString(buffer) != "FORM")
      {
        throw new InvalidDataException("Form header not found.");
      }

      // the next value is the size of all the data in the FORM chunk
      // We don't actually need this value, but we have to read it
      // regardless to advance the stream
      this.ReadInt32(stream);

      // read either the PBM or ILBM header that identifies this document as an image file
      stream.Read(buffer, 0, buffer.Length);
      header = Encoding.ASCII.GetString(buffer);
      if (header != "PBM " && header != "ILBM")
      {
        throw new InvalidDataException("Bitmap header not found.");
      }

      while (stream.Read(buffer, 0, buffer.Length) == buffer.Length)
      {
        int chunkLength;

        chunkLength = this.ReadInt32(stream);

        if (Encoding.ASCII.GetString(buffer) != "CMAP")
        {
          // some other LBM chunk, skip it
          if (stream.CanSeek)
          {
            stream.Seek(chunkLength, SeekOrigin.Current);
          }
          else
          {
            for (int i = 0; i < chunkLength; i++)
            {
              stream.ReadByte();
            }
          }
        }
        else
        {
          // color map chunk!
          for (int i = 0; i < chunkLength / 3; i++)
          {
            int r;
            int g;
            int b;

            r = stream.ReadByte();
            g = stream.ReadByte();
            b = stream.ReadByte();

            results.Add(Color.FromArgb(r, g, b));
          }

          // all done so stop reading the rest of the file
          break;
        }

        // chunks always contain an even number of bytes even if the recorded length is odd
        // if the length is odd, then there's a padding byte in the file - just read and discard
        if (chunkLength % 2 != 0)
        {
          stream.ReadByte();
        }
      }

      return results;
    }

    /// <summary>
    /// Serializes the specified <see cref="ColorCollection" /> and writes the palette to a file using the specified <see cref="Stream" />.
    /// </summary>
    /// <param name="stream">The <see cref="Stream" /> used to write the palette.</param>
    /// <param name="palette">The <see cref="ColorCollection" /> to serialize.</param>
    public override void Serialize(Stream stream, ColorCollection palette)
    {
      if (stream == null)
      {
        throw new ArgumentNullException("stream");
      }

      if (palette == null)
      {
        throw new ArgumentNullException("palette");
      }

      throw new NotSupportedException();
    }

    #endregion
  }
}
