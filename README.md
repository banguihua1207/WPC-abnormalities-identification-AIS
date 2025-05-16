# WPC Abnormal Data Identification Method - AIS

Abnormal data recognition method for wind turbines based on alpha
channel fusion

<p align="center">
<img src=".\pic\AIS.svg" height = "250" alt="" align=center />
<br><br>
<b>Figure 1.</b> Overall architecture of AIS.
</p>

## Get Started

1. Install Python 3.6.
2. Download data. You can obtain all the 134 datasets from [Baidu KDD CUP 2022](https://aistudio.baidu.com/competition/detail/152/0/introduction)
3. Requirements: opencv==4.3.0.38, tsmoothie==1.0.4.
4. Run whole_procedule.py.
5. Supplementary explanation: For your own WPC data, the identification and cleaning of type I abnormal data can be achieved through 
the **data_image.py** file, and the input image of **whole_procedule.py** can be obtained. Then, the classification and identification of WPC abnormal data are achieved by adjusting the two parameters, **alph_th** and **line_th**.

## Citation

If you find this repo useful, please cite our paper. 

```
@inproceedings{chen2025abnormal,
  title={Abnormal data recognition method for wind turbines based on alpha
channel fusion},
  author={Yan Chen and Guihua Ban and Tingxiao Ding},
  ...,
  year={2025}
}
```

## Contact
If you have any question or want to use the code, please contact bansemail@163.com.