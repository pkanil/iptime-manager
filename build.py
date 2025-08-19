#!/usr/bin/env python3
"""
Build script for creating standalone executable
"""
import os
import sys
import shutil
import subprocess

def build_executable():
    """PyInstaller를 사용하여 실행 파일 생성"""
    
    # PyInstaller 명령어 옵션
    options = [
        'iptime_cli.py',                    # 메인 스크립트
        '--name', 'iptime-manager',         # 실행 파일 이름
        '--onefile',                         # 단일 파일로 생성
        '--clean',                           # 빌드 전 캐시 정리
        '--noconfirm',                       # 덮어쓰기 확인 없음
        '--add-data', 'src:src',            # src 디렉토리 포함
        '--hidden-import', 'requests',      # 숨겨진 임포트 명시
        '--hidden-import', 'urllib3',
        '--hidden-import', 'certifi',
        '--hidden-import', 'charset_normalizer',
        '--hidden-import', 'idna',
    ]
    
    # Linux/Unix 환경에서 추가 옵션
    if sys.platform in ['linux', 'linux2', 'darwin']:
        options.extend([
            '--strip',                      # 심볼 제거 (파일 크기 감소)
        ])
    
    print("Building executable with PyInstaller...")
    print(f"Command: pyinstaller {' '.join(options)}")
    
    try:
        # PyInstaller 실행
        subprocess.run(['pyinstaller'] + options, check=True)
        
        # 빌드 결과 확인
        if sys.platform == 'win32':
            exe_path = 'dist/iptime-manager.exe'
        else:
            exe_path = 'dist/iptime-manager'
            
        if os.path.exists(exe_path):
            # 파일 크기 확인
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n✅ Build successful!")
            print(f"📦 Executable: {exe_path}")
            print(f"📊 Size: {size_mb:.2f} MB")
            
            # 실행 권한 부여 (Linux/Mac)
            if sys.platform in ['linux', 'linux2', 'darwin']:
                os.chmod(exe_path, 0o755)
                print(f"🔧 Executable permissions set")
            
            return True
        else:
            print("❌ Build failed: Executable not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found. Install it with: pip install pyinstaller")
        return False

def clean_build_artifacts():
    """빌드 아티팩트 정리"""
    artifacts = ['build', '__pycache__', 'iptime-manager.spec']
    
    for artifact in artifacts:
        if os.path.exists(artifact):
            if os.path.isdir(artifact):
                shutil.rmtree(artifact)
            else:
                os.remove(artifact)
            print(f"🧹 Cleaned: {artifact}")

if __name__ == "__main__":
    print("🚀 iptime-manager Build Script")
    print("=" * 50)
    
    # 빌드 실행
    success = build_executable()
    
    if success:
        print("\n" + "=" * 50)
        print("✨ Build completed successfully!")
        print("\nTo run the executable:")
        if sys.platform == 'win32':
            print("  ./dist/iptime-manager.exe --help")
        else:
            print("  ./dist/iptime-manager --help")
        
        # 빌드 아티팩트 정리 옵션
        response = input("\nClean build artifacts? (y/n): ")
        if response.lower() == 'y':
            clean_build_artifacts()
    else:
        print("\n💔 Build failed. Please check the errors above.")
        sys.exit(1)