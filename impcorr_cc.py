import numpy as np
import pandas as pd
   

class impcorr_cc:

    def __init__(self, yj, yk, lbls = list()):
        """
        Use the "order" object for the sklearn module: ClassifierChain(base_lr, order=order, random_state=0) 
        """
        self.label_data = lbls

        self.isu_mtrx = np.empty([len(lbls), len(lbls)])

        for n, j in enumerate(lbls):
            for m, k in enumerate(lbls):
                #print(n,m)
                if j != k:
                    #print(j,k)
                    self.isu_mtrx[n][m] = self.ISU(j, k)
                else:
                    self.isu_mtrx[n][m] = 0
        
        self.order = self.determine_label_order(self.label_data, self.isu_mtrx)


    def shannon_entropy(self, prob) -> float:
        """
        :param prob: Probability to compute Shannon Entropy
        :type: float
        """

        return -1*prob*np.log2(prob) - (1-prob)*np.log2(1 - prob)

    def P_cond(self, yj, yk) -> float:
        """
        :param yj: label of interest, y_j
        :type: str
        :param yk: label of interest, y_k
        :type: str
        """

        both = sum(self.label_data[yj] & self.label_data[yk]) #where label yj and yk are relevent
        k = sum(self.label_data[yk].astype(bool) & ~self.label_data[yj].astype(bool)) #where yk but not yj
        nk = sum(self.label_data[yk].astype(bool))

        if np.abs(both - k) <= 2:
            return 0.5
        elif both > k + 2:
            return (both - 1)/nk
        elif k > both + 2:
            return (both + 1)/nk
        else:
            return 0
        
    def P_relev(self, yj) -> float:

        """
        :param yj: label of interest, y_j
        :type: str
        """

        nj = sum(self.label_data[yj].astype(bool))
        nj_not = sum(~self.label_data[yj].astype(bool))
        N = len(self.label_data)

        if np.abs(nj - nj_not) <=2:
            return 0.5
        elif nj > nj_not + 2:
            return (nj - 1)/N
        elif nj_not > nj + 2:
            return (nj + 1)/N
        else:
            return 0
        
    def P_mean(self, yj, yk) -> float:
        """
        :param yj: label of interest, y_j
        :type: str
        :param yk: label of interest, y_k
        :type: str
        """

        j = sum(~self.label_data[yk].astype(bool) & self.label_data[yj].astype(bool)) #where yj but not yk
        neither = sum(~self.label_data[yk].astype(bool) & ~self.label_data[yj].astype(bool)) #neither relevant
        nk_not = sum(~self.label_data[yk].astype(bool))

        if np.abs(j - neither) <= 2:
            return 0.5
        elif j > neither + 2:
            return (j - 1)/nk_not
        elif neither > j + 2:
            return (j + 1)/nk_not
        
    def IIG(self, yj, yk) -> float:
        """
        Imprecise Information Gain, based on Kullback–Leibler divergence.

        :param yj: label of interest, y_j
        :type: str
        :param yk: label of interest, y_k
        :type: str
        """
    
        Sp_j = self.shannon_entropy(self.P_relev(yj))
        p_k = self.P_relev(yk)
        Spcond = self.shannon_entropy(self.P_cond(yj, yk))
        Spbar = self.shannon_entropy(self.P_mean(yj, yk))
        
        return Sp_j - p_k*Spcond - (1 - p_k)*Spbar

    def ISU(self, yj, yk) -> float:
        """
        Imprecise Symmetrical Uncertainty (ISU). Normalizes the IIG to estimate the correlation of two variables.

        :param yj: label of interest, y_j
        :type: str
        :param yk: label of interest, y_k
        :type: str
        """
        denom = self.shannon_entropy(self.P_relev(yj)) + self.shannon_entropy(self.P_relev(yk))

        return 2 * self.IIG(yj, yk)/denom
    
    def determine_label_order(self, lbls, corr) -> list:
        lbl_order = [None] * len(lbls) #to save final order
        score = [np.nan] * len(lbls) #to iterate over

        for j in range(0, len(lbls), 1): #first item in label list
            score[j] = np.sum(corr[j]) #row j in a matrix
        lbl_order[0] = np.nanargmax(score)

        for i in range(1, len(lbls), 1): #where in the order we'll be
            score = [np.nan] * len(lbls) #to iterate over
            leftover = [l for l in range(0, len(lbls), 1) if l not in lbl_order] #indices of labels left

            for j in leftover:
                #print(lbl_order)
                in_list = [corr[j][k] for k in lbl_order if k is not None] #correlation with labels alr in the list
                out_list = [corr[j][k] for k in leftover] #correlation with labels not in the list
                score[j] = (np.sum(in_list))/(len(lbls) - i) + (np.sum(out_list))/(len(leftover))

            lbl_order[i] = np.nanargmax(score)

        return lbl_order