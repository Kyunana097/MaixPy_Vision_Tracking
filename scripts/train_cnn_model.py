#!/usr/bin/env python3
"""
CNN人脸识别模型训练脚本
用于PC端预训练，然后部署到MaixCAM
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
import torchvision.models as models
from torch.utils.data import Dataset, DataLoader
import os
import json
import numpy as np
from PIL import Image
import argparse

class FaceDataset(Dataset):
    """人脸数据集类"""
    
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.images = []
        self.labels = []
        self.label_to_name = {}
        
        # 扫描数据目录
        label_id = 0
        for person_name in os.listdir(data_dir):
            person_dir = os.path.join(data_dir, person_name)
            if os.path.isdir(person_dir):
                self.label_to_name[label_id] = person_name
                
                for img_file in os.listdir(person_dir):
                    if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        img_path = os.path.join(person_dir, img_file)
                        self.images.append(img_path)
                        self.labels.append(label_id)
                
                label_id += 1
        
        print(f"✓ 加载数据集: {len(self.images)} 张图片, {len(self.label_to_name)} 个人物")
        for label_id, name in self.label_to_name.items():
            count = self.labels.count(label_id)
            print(f"  - {name}: {count} 张图片")
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_path = self.images[idx]
        label = self.labels[idx]
        
        # 加载图像
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

class FaceEncoder(nn.Module):
    """轻量化人脸特征编码器"""
    
    def __init__(self, num_classes, feature_dim=128):
        super(FaceEncoder, self).__init__()
        
        # 使用预训练的MobileNetV2作为骨干网络
        self.backbone = models.mobilenet_v2(pretrained=True)
        
        # 替换分类头
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(1280, feature_dim),
            nn.ReLU(inplace=True),
            nn.Linear(feature_dim, num_classes)
        )
        
        # 特征提取器（用于部署）
        self.feature_extractor = nn.Sequential(
            self.backbone.features,
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Dropout(0.2),
            nn.Linear(1280, feature_dim)
        )
    
    def forward(self, x):
        return self.backbone(x)
    
    def extract_features(self, x):
        """提取特征向量（用于相似度计算）"""
        features = self.feature_extractor(x)
        return F.normalize(features, p=2, dim=1)

def create_data_transforms():
    """创建数据变换"""
    train_transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.RandomHorizontalFlip(p=0.3),
        transforms.RandomRotation(degrees=10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    return train_transform, val_transform

def train_model(data_dir, output_dir, epochs=50, batch_size=16, lr=0.001):
    """训练模型"""
    
    print("🚀 开始训练CNN人脸识别模型...")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 数据变换
    train_transform, val_transform = create_data_transforms()
    
    # 加载数据集
    dataset = FaceDataset(data_dir, train_transform)
    
    # 数据集划分
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
    
    # 为验证集应用不同的变换
    val_dataset.dataset.transform = val_transform
    
    # 数据加载器
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # 模型
    num_classes = len(dataset.label_to_name)
    model = FaceEncoder(num_classes)
    
    # 设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    print(f"✓ 使用设备: {device}")
    
    # 损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=20, gamma=0.5)
    
    # 训练循环
    best_acc = 0.0
    
    for epoch in range(epochs):
        # 训练阶段
        model.train()
        train_loss = 0.0
        train_correct = 0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            pred = output.argmax(dim=1, keepdim=True)
            train_correct += pred.eq(target.view_as(pred)).sum().item()
        
        # 验证阶段
        model.eval()
        val_loss = 0.0
        val_correct = 0
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                val_loss += criterion(output, target).item()
                pred = output.argmax(dim=1, keepdim=True)
                val_correct += pred.eq(target.view_as(pred)).sum().item()
        
        # 计算准确率
        train_acc = 100. * train_correct / len(train_dataset)
        val_acc = 100. * val_correct / len(val_dataset)
        
        print(f'Epoch {epoch+1}/{epochs}:')
        print(f'  训练 - Loss: {train_loss/len(train_loader):.4f}, Acc: {train_acc:.2f}%')
        print(f'  验证 - Loss: {val_loss/len(val_loader):.4f}, Acc: {val_acc:.2f}%')
        
        # 保存最佳模型
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save({
                'model_state_dict': model.state_dict(),
                'label_to_name': dataset.label_to_name,
                'feature_dim': 128,
                'num_classes': num_classes
            }, os.path.join(output_dir, 'best_face_model.pth'))
            print(f'  ✓ 保存最佳模型 (验证准确率: {best_acc:.2f}%)')
        
        scheduler.step()
        print()
    
    print(f"🎯 训练完成! 最佳验证准确率: {best_acc:.2f}%")
    
    # 保存标签映射
    with open(os.path.join(output_dir, 'label_mapping.json'), 'w') as f:
        json.dump(dataset.label_to_name, f, indent=2, ensure_ascii=False)
    
    return model, dataset.label_to_name

def export_for_maixpy(model_path, output_dir):
    """导出模型用于MaixPy部署"""
    
    print("📦 导出模型用于MaixPy部署...")
    
    # 加载训练好的模型
    checkpoint = torch.load(model_path, map_location='cpu')
    
    model = FaceEncoder(checkpoint['num_classes'], checkpoint['feature_dim'])
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    # 创建示例输入
    dummy_input = torch.randn(1, 3, 64, 64)
    
    # 导出ONNX模型
    onnx_path = os.path.join(output_dir, 'face_encoder.onnx')
    torch.onnx.export(
        model.feature_extractor,  # 只导出特征提取部分
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['features'],
        dynamic_axes={'input': {0: 'batch_size'}, 'features': {0: 'batch_size'}}
    )
    
    print(f"✓ ONNX模型已保存: {onnx_path}")
    print("📝 下一步:")
    print("  1. 将ONNX模型转换为MaixPy支持的.mud格式")
    print("  2. 将模型文件复制到MaixCAM的/root/models/目录")
    print("  3. 更新MaixPy代码以使用CNN特征提取")

def main():
    parser = argparse.ArgumentParser(description='训练CNN人脸识别模型')
    parser.add_argument('--data_dir', type=str, required=True,
                      help='训练数据目录路径')
    parser.add_argument('--output_dir', type=str, default='./trained_models',
                      help='模型输出目录')
    parser.add_argument('--epochs', type=int, default=50,
                      help='训练轮数')
    parser.add_argument('--batch_size', type=int, default=16,
                      help='批次大小')
    parser.add_argument('--lr', type=float, default=0.001,
                      help='学习率')
    
    args = parser.parse_args()
    
    # 训练模型
    model, label_mapping = train_model(
        args.data_dir, 
        args.output_dir, 
        args.epochs, 
        args.batch_size, 
        args.lr
    )
    
    # 导出用于部署
    model_path = os.path.join(args.output_dir, 'best_face_model.pth')
    export_for_maixpy(model_path, args.output_dir)

if __name__ == '__main__':
    main()
