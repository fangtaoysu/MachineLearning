import torch
from torchvision import transforms
from torchvision import datasets
from torch.utils.data import  DataLoader
import torch.nn.functional as F #使用functional中的ReLu激活函数
import torch.optim as optim


class Net(torch.nn.Module):
    def __init__(self, train_loader, test_loader):
        super(Net, self).__init__()
        self.train_loader = train_loader
        self.test_loader = test_loader
        # 两个卷积层
        self.conv1 = torch.nn.Conv2d(1, 10, kernel_size=5)  # 1为in_channels 10为out_channels
        self.conv2 = torch.nn.Conv2d(10, 20, kernel_size=5)
        # 池化层
        self.pooling = torch.nn.MaxPool2d(2)  # 2为分组大小2*2
        # 全连接层 320 = 20 * 4 * 4
        self.fc = torch.nn.Linear(320, 10)

    def forward(self, x):
        '''前向传播'''
        # 先从x数据维度中得到batch_size
        batch_size = x.size(0)
        # 卷积层->池化层->激活函数
        x = F.relu(self.pooling(self.conv1(x)))
        x = F.relu(self.pooling(self.conv2(x)))
        x = x.view(batch_size, -1)  # 将数据展开，为输入全连接层做准备
        x = self.fc(x)
        return x

    def train(self, epoch):
        '''用训练集训练cnn'''
        running_loss = 0.0
        for batch_idx, data in enumerate(self.train_loader, 0):   # 在这里data返回输入:inputs、输出target
            inputs, target = data
            optimizer.zero_grad()
            # 前向 + 反向 + 更新
            outputs = model(inputs)
            loss = criterion(outputs, target)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            if batch_idx % 300 == 299:
                print('[%d, %5d] loss: %.3f' % (epoch + 1, batch_idx + 1, running_loss / 300))

    def test(self):
        '''用测试集测试训练好的数据'''
        correct = 0
        total = 0
        with torch.no_grad():  # 不需要计算梯度
            for data in self.test_loader:   # 遍历数据集中的每一个batch
                images, labels = data  # 保存测试的输入和输出
                outputs = model(images) # 得到预测输出
                _, predicted = torch.max(outputs.data, dim=1) # dim=1沿着索引为1的维度(行)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        print(f'测试集的精确率为:{100. * correct / total:.2f}%')

def load_data():
    '''数据的准备'''
    batch_size = 64
    # 神经网络希望输入的数值较小，最好在0-1之间，所以需要先将原始图像(0-255的灰度值)转化为图像张量（值为0-1）
    # 仅有灰度值->单通道   RGB -> 三通道 读入的图像张量一般为W*H*C (宽、高、通道数) 在pytorch中要转化为C*W*H
    transform = transforms.Compose([
        # 将数据转化为图像张量
        transforms.ToTensor(),
        # 进行归一化处理，切换到0-1分布 （均值， 标准差）
        transforms.Normalize((0.1307, ), (0.3081, ))
    ])
    train_dataset = datasets.MNIST(root='../dataset/mnist/',train=True,download=True,transform=transform)
    train_loader = DataLoader(train_dataset,shuffle=True,batch_size=batch_size)
    test_dataset = datasets.MNIST(root='../dataset/mnist/',train=False,download=True,transform=transform)
    test_loader = DataLoader(test_dataset,shuffle=False,batch_size=batch_size)
    return train_loader, test_loader

if __name__ == '__main__':
    # 准备数据
    train_loader, test_loader = load_data()
    model = Net(train_loader, test_loader)
    # 设置损失函数和优化器
    criterion = torch.nn.CrossEntropyLoss()
    # 神经网络已经逐渐变大，需要设置冲量momentum=0.5
    optimizer = optim.SGD(model.parameters(), lr=0.03, momentum=0.5)
    for epoch in range(3):
        model.train(epoch)
        model.test()
