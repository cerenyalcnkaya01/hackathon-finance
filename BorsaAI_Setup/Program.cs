using System;
using System.Diagnostics;
using System.IO;

namespace BorsaAI.Setup
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("========================================");
            Console.WriteLine("    Borsa AI — Kurulum Sihirbazı");
            Console.WriteLine("========================================");
            Console.WriteLine();

            if (!CheckPython())
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("HATA: Python 3.11 veya üzeri yüklü değil!");
                Console.ResetColor();
                Console.WriteLine("Lütfen python.org adresinden Python yükleyin ve 'Add to PATH' seçeneğini işaretleyin.");
                Console.WriteLine("\nDevam etmek için bir tuşa basın...");
                Console.ReadKey();
                return;
            }

            InstallRequirements();
            CheckOllama();
            
            Console.WriteLine();
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine("Kurulum tamamlandı! Artık BorsaAI uygulamasını kullanabilirsiniz.");
            Console.ResetColor();
            Console.WriteLine("\nKapatmak için bir tuşa basın...");
            Console.ReadKey();
        }

        static bool CheckPython()
        {
            Console.WriteLine("[1/3] Python kontrol ediliyor...");
            try
            {
                var p = Process.Start(new ProcessStartInfo {
                    FileName = "python", Arguments = "--version", 
                    RedirectStandardOutput = true, UseShellExecute = false, CreateNoWindow = true
                });
                p?.WaitForExit();
                string? output = p?.StandardOutput.ReadToEnd();
                Console.WriteLine($"  Bulunan: {output?.Trim() ?? "Bilinmiyor"}");
                return p?.ExitCode == 0;
            }
            catch { return false; }
        }

        static void InstallRequirements()
        {
            Console.WriteLine("[2/3] Kütüphaneler kuruluyor (pip install)...");
            string rootDir = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, ".."));
            string reqPath = Path.Combine(rootDir, "requirements.txt");

            if (!File.Exists(reqPath))
            {
                 // Try current dir if not in parent
                 rootDir = AppDomain.CurrentDomain.BaseDirectory;
                 reqPath = Path.Combine(rootDir, "requirements.txt");
            }

            try
            {
                var p = Process.Start(new ProcessStartInfo {
                    FileName = "python", 
                    Arguments = "-m pip install -r \"" + reqPath + "\"",
                    UseShellExecute = false
                });
                p?.WaitForExit();
                Console.WriteLine("  Kütüphane kurulumu bitti.");
            }
            catch (Exception ex) { Console.WriteLine($"  HATA: {ex.Message}"); }
        }

        static void CheckOllama()
        {
            Console.WriteLine("[3/3] AI Modeli (llama3.1) indiriliyor...");
            try
            {
                var p = Process.Start(new ProcessStartInfo {
                    FileName = "ollama", Arguments = "pull llama3.1",
                    UseShellExecute = false
                });
                p?.WaitForExit();
                Console.WriteLine("  Model hazır.");
            }
            catch
            {
                Console.WriteLine("  UYARI: Ollama bulunamadı veya model indirilemedi.");
                Console.WriteLine("  Lütfen Ollama'nın yüklü olduğundan emin olun.");
            }
        }
    }
}
