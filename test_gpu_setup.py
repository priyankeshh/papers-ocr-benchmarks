
# GPU Test Script - Auto-generated
import torch
print("🧪 QUICK GPU TEST")
print("=" * 30)
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    # Quick computation test
    x = torch.randn(100, 100).cuda()
    y = x @ x.T
    print("✅ GPU computation successful!")
    
    torch.cuda.empty_cache()
else:
    print("⚠️  Using CPU mode")

print("\n🎯 Ready for OCR benchmarking!")
