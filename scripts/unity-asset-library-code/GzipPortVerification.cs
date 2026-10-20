using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;

// Interface-only fixture avoids loading/executing a vendor DLL. The actual local
// hash-checked compression candidate is compiled beside this authored test.
namespace GameFramework
{
    public static class Utility
    {
        public static class Compression
        {
            public interface ICompressionHelper
            {
                bool Compress(byte[] bytes, int offset, int length, Stream output);
                bool Compress(Stream input, Stream output);
                bool Decompress(byte[] bytes, int offset, int length, Stream output);
                bool Decompress(Stream input, Stream output);
            }
        }
    }
}

static class GzipPortVerification
{
    static int assertions;
    static void Require(bool condition, string message)
    {
        assertions++;
        if (!condition) throw new InvalidOperationException(message);
    }
    static void CheckHeader(byte[] encoded)
    {
        Require(encoded.Length >= 18, "GZip header/trailer missing");
        Require(encoded[0] == 31 && encoded[1] == 139 && encoded[2] == 8, "GZip signature changed");
        Require(encoded.Skip(4).Take(4).SequenceEqual(new byte[] { 25, 134, 2, 32 }), "Fixed MTIME header changed");
    }
    static int Main(string[] args)
    {
        var helper = new UnityGameFramework.Runtime.DefaultCompressionHelper();
        foreach (int length in new[] { 0, 1, 4097, 131071 })
        {
            var bytes = new byte[length]; new Random(41 + length).NextBytes(bytes);
            foreach (bool compressStream in new[] { false, true })
            {
                using var source = new MemoryStream(bytes);
                using var encoded = new MemoryStream();
                var padded = new byte[length + 16]; Array.Copy(bytes, 0, padded, 7, length);
                Require(compressStream ? helper.Compress(source, encoded) : helper.Compress(padded, 7, length, encoded), "Compress failed");
                Require(source.CanRead && encoded.CanWrite, "Compression closed a caller stream");
                byte[] gzip = encoded.ToArray(); CheckHeader(gzip);
                foreach (bool decompressStream in new[] { false, true })
                {
                    using var input = new MemoryStream(gzip);
                    using var output = new MemoryStream();
                    var framed = new byte[gzip.Length + 20]; Array.Copy(gzip, 0, framed, 9, gzip.Length);
                    Require(decompressStream ? helper.Decompress(input, output) : helper.Decompress(framed, 9, gzip.Length, output), "Decompress failed");
                    Require(output.ToArray().SequenceEqual(bytes), "Roundtrip payload mismatch");
                    Require(input.CanRead && output.CanWrite, "Decompression closed a caller stream");
                }
            }
        }
        using var destination = new MemoryStream();
        Require(!helper.Compress((byte[])null, 0, 0, destination), "Null input behavior changed");
        Require(!helper.Compress(new byte[2], 1, 2, destination), "Range validation changed");
        using var broken = new MemoryStream(Encoding.ASCII.GetBytes("invalid gzip payload"));
        Require(!helper.Decompress(broken, destination), "Corrupt payload should fail");
        Require(broken.CanRead && destination.CanWrite, "Failure closed caller streams");
        var report = new { passed = true, assertions, combinations = 16, fixedMtimeVerified = true, callerStreamsRemainOpen = true,
            vendorAssemblyExecuted = false, test = "Actual adapted candidate + interface-only fixture; empty/one-byte/buffer-boundary/large/random/offset/corrupt payloads." };
        File.WriteAllText(args[0], JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true }));
        Console.WriteLine(JsonSerializer.Serialize(report));
        return 0;
    }
}
