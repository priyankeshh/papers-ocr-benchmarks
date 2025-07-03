#!/usr/bin/env python3
"""
GPU Environment Setup and Verification Script
For OCR Benchmark 
Author: Priyankesh

This script helps setup and verify GPU environment for optimal OCR benchmarking.
"""

import sys
import subprocess
import importlib.util

def check_package(package_name):
    """Check if a package is installed"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_package(package_name, pip_name=None):
    """Install a package using pip"""
    if pip_name is None:
        pip_name = package_name
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        return True
    except subprocess.CalledProcessError:
        return False

def check_gpu_environment():
    """Comprehensive GPU environment check"""
    print("🔍 GPU ENVIRONMENT DIAGNOSTIC")
    print("=" * 50)
    
    # Check basic packages
    packages = {
        'torch': 'torch',
        'numpy': 'numpy', 
        'pandas': 'pandas',
        'matplotlib': 'matplotlib'
    }
    
    missing_packages = []
    for package, pip_name in packages.items():
        if check_package(package):
            print(f"✅ {package} installed")
        else:
            print(f"❌ {package} missing")
            missing_packages.append(pip_name)
    
    # Install missing packages
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            if install_package(package):
                print(f"✅ Installed {package}")
            else:
                print(f"❌ Failed to install {package}")
    
    # Check PyTorch and CUDA
    print(f"\n🔥 PYTORCH & CUDA CHECK")
    print("-" * 30)
    
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        
        # CUDA availability
        cuda_available = torch.cuda.is_available()
        print(f"🚀 CUDA available: {cuda_available}")
        
        if cuda_available:
            print(f"   GPU count: {torch.cuda.device_count()}")
            print(f"   Current device: {torch.cuda.current_device()}")
            print(f"   Device name: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA version: {torch.version.cuda}")
            
            # Memory info
            total_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"   Total GPU memory: {total_memory:.1f} GB")
            
            # Test GPU functionality
            try:
                x = torch.randn(1000, 1000).cuda()
                y = torch.randn(1000, 1000).cuda()
                z = torch.mm(x, y)
                print("✅ GPU computation test: PASSED")
                
                # Clear test tensors
                del x, y, z
                torch.cuda.empty_cache()
                
            except Exception as e:
                print(f"❌ GPU computation test: FAILED - {e}")
        else:
            print("⚠️  GPU not available - will use CPU mode")
            print("   For GPU acceleration:")
            print("   1. Install NVIDIA drivers")
            print("   2. Install CUDA toolkit")
            print("   3. Install GPU-enabled PyTorch:")
            print("      pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
    
    except ImportError:
        print("❌ PyTorch not installed")
        print("Installing PyTorch...")
        
        # Try to install PyTorch with CUDA support
        cuda_install_cmd = "torch torchvision --index-url https://download.pytorch.org/whl/cu118"
        if install_package("torch", cuda_install_cmd):
            print("✅ PyTorch with CUDA installed")
        else:
            # Fallback to CPU version
            if install_package("torch"):
                print("✅ PyTorch (CPU) installed")
            else:
                print("❌ Failed to install PyTorch")
    
    # Check OCR-specific packages
    print(f"\n📄 OCR PACKAGES CHECK")
    print("-" * 30)
    
    ocr_packages = {
        'fitz': 'PyMuPDF',
        'marker': 'marker-pdf',
        'docling': 'docling',
        'textdistance': 'textdistance'
    }
    
    for package, pip_name in ocr_packages.items():
        if check_package(package):
            print(f"✅ {package} installed")
        else:
            print(f"❌ {package} missing - installing...")
            if install_package(package, pip_name):
                print(f"✅ Installed {package}")
            else:
                print(f"❌ Failed to install {package}")

def generate_optimal_config():
    """Generate optimal configuration for the current system"""
    print(f"\n⚙️  OPTIMAL CONFIGURATION")
    print("-" * 30)
    
    try:
        import torch
        
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            total_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            
            print("🚀 GPU Configuration Recommended:")
            print(f"   Device: {device_name}")
            print(f"   Memory: {total_memory:.1f} GB")
            print("   Use: ocr_benchmark_gpu_optimized.py")
            print("   Settings:")
            print("     - torch.backends.cudnn.benchmark = True")
            print("     - pin_memory = True")
            print("     - GPU memory management enabled")
            
            # Recommend batch size based on memory
            if total_memory >= 8:
                print("     - Recommended: Process all documents")
            elif total_memory >= 4:
                print("     - Recommended: Process 1-2 documents at a time")
            else:
                print("     - Recommended: Use CPU mode for large documents")
        else:
            print("💻 CPU Configuration Recommended:")
            print("   Use: ocr_benchmark_notebook_clean.py")
            print("   Settings:")
            print("     - Sequential processing")
            print("     - Monitor RAM usage")
            print("     - Consider processing fewer documents")
    
    except ImportError:
        print("❌ Cannot generate config - PyTorch not available")

def create_test_script():
    """Create a simple test script to verify setup"""
    test_script = '''
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

print("\\n🎯 Ready for OCR benchmarking!")
'''
    
    with open('test_gpu_setup.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print(f"\n📝 Created test_gpu_setup.py")
    print("   Run: python test_gpu_setup.py")

def main():
    """Main setup function"""
    print("🚀 OCR BENCHMARK GPU SETUP")
    print("=" * 50)
    print("Setting up optimal environment for OCR benchmarking...")
    print()
    
    # Run all checks
    check_gpu_environment()
    generate_optimal_config()
    create_test_script()
    
    print(f"\n🎉 SETUP COMPLETE!")
    print("=" * 50)
    print("Next steps:")
    print("1. Run: python test_gpu_setup.py")
    print("2. If GPU available: python ocr_benchmark_gpu_optimized.py")
    print("3. If CPU only: python ocr_benchmark_notebook_clean.py")
    print("4. Check BENCHMARK_DOCUMENTATION.md for detailed instructions")

if __name__ == "__main__":
    main()
