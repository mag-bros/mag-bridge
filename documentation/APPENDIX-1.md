## Appendix 1. Constitutive corrections (&lambda;<sub>i</sub>) - bond type query

> [!NOTE]
> ## Author Notes for Users
>
>As creators of the open-source MagBridge project, our primary goal is to develop a reliable tool for processing magnetic measurement data. We therefore invite you to contribute to the further development of MagBridge by sharing your feedback and suggestions. We hope this project grows into a space where experts and researchers from different fields come together to share their knowledge and experience to build a tool that advances scientific discovery.
>
> #### We welcome any comments on the approaches we have adopted. If you identify potential issues or areas for improvement, you are warmly invited to contact us via email: [kpwydra@gmail.com](mailto:kpwydra@gmail.com)

&nbsp;

The diamagnetic contribution for a given compound may be estimated by summing atomic susceptibilities (**&chi;<sub>Di</sub>**) and *constitutive corrections* (**&lambda;<sub>i</sub>**):

$$
\chi_D = \sum_i \chi_{Di} + \sum_i \lambda_i \quad
$$

<p align="right">
 <span id="eq1"> (A.1)</span>
</p>

where **&lambda;<sub>i</sub>** takes into account the fact that compounds with multiple bonds exhibit weaker diamagnetic susceptibility than saturated compounds with only single bonds. A single **&lambda;<sub>i</sub>** constant can account for either an individual bond between a pair of atoms or larger structural fragments of a molecule (e.g., rings, functional groups, or conjugated systems), collectively referred to as *bond types*.

There is significant confusion regarding the &lambda;<sub>i</sub> and &chi;<sub>Di</sub> constants, arising from conflicting values reported across different sources. To avoid inconsistencies in the data used in MagBridge, the constitutive corrections implemented in the software were taken exclusively from the article by G. A. Bain et al.[ref], which provides a valuable clarification of this issue. Because constitutive corrections have been tabulated for only a limited number of bond types, they do not adequately capture the enormous structural diversity of organic and inorganic compounds. In turn, this may reduce the accuracy of calculating the overall diamagnetic contribution of the compound (**Comment: here, some discussion on how the final result may affect the data may be added in the future**).

Due to the scarcity of the literature constitutive correction data, the assignment of available bond types for certain molecules was nontrivial and required several assumptions, which are discussed herein. Two opposite approaches could be made to overcome this issue. The first is a strict approach, applying &lambda;<sub>i</sub> to exactly corresponding bond types. The second is a more flexible approach, in which a given constitutive correction is assumed to also apply to structurally similar fragments. During software development, we chose to follow the second approach. However, in a future iteration of the software, the user will be able to decide whether the automatic application of constitutive corrections for a studied compound is appropriate and, if necessary, adjust them manually during postprocessing.

### Linear Conjugated Polyenes

<p align="center">
<img src="https://github.com/user-attachments/assets/0d276288-0355-408d-b37f-a242f224b623" alt="Image" width="600">
</p>
<p align="center">
  <b>Figure A.1</b> An example of bond type assignment for a linear conjugated polyene.
</p>

To account for linear conjugated polyene fragments containing three or more conjugated C=C bonds, we assumed that the constitutive correction for such a fragment can be approximated as the sum of the corrections for the relevant, available bond types C=C, Ar-C=C, and/or C=C-C=C (Figure A.1).

### Carboxyl group

The available constitutive corrections account only for Ar-COOH and RCOOH carboxyl fragments, with the carboxyl group in its neutral form. However, in ligands of paramagnetic coordination compounds, the carboxyl group is usually deprotonated. For these reasons, we assumed that the literature constitutive correction of $\lambda_{RCOOH} = -5.0 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}$ for RCOOH fragment can also be applied to the deprotonated fragment RCOO-. Analogously, the $\lambda_{Ar-COOH} = -1.5 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}$ was assumed to be relevant for Ar-COO- fragment.

### Phenol group
As with the carboxyl group, the Ar–OH constitutive correction was also assumed to represent the deprotonated phenolate (Ar–O<sup>-</sup>) group.

### N-heterocyclic rings
For the reasons explained for the carboxyl group, constitutive correction for a given ring in its neutral protonation state was also assumed to be relevant for other common protonation states of the ring. The relevant rings are: imidazole, pyrazine, pyrimidine, pyridine, pyrrole, 1,3,5-triazine, thiazole, pyrrolidine, piperidine and piperazine. 

It is important to note that for some rings (including saturated ones), the constitutive corrections are unavailable.

### Ester group
Two relevant constitutive corrections &lambda;<sub>i</sub> are available, one corresponding to RCOOR and the second to the Ar-COOR group. We permitted &lambda;<sub>RCOOR</sub> to also be applied when the R group bonded to oxygen atom is substituted with aryl groups or N, O, or Si atoms. The same assumption was made for the &lambda;<sub>Ar-COOR</sub> of Ar-COOR group.

Another dilemma was the acid anhydride R-C(=O)-O-C(=O)-R' fragment, which has no associated constitutive correction. To address this issue, we decided to use two constitutive corrections corresponding to ester bond types (RCOOR or Ar-COOR), as these have the closest structural resemblance among the available bond types (Figure A.2). Omitting R-C(=O)-O-C(=O)-R' fragment without applying any &lambda;<sub>i</sub> constant would presumably result in a greater systematic error than applying the constitutive correction of a similar bond type.

<p align="center">
<img  src="https://github.com/user-attachments/assets/aa5ff399-fe72-44ff-88df-4a7f195edf16" alt="Image" width="200">
</p>
<p align="center">
  <b>Figure A.2</b> Two &lambda;<sub>i</sub> constants corresponding to ester group are used to account for acid anhydride R-C(=O)-O-C(=O)-R' fragment.
</p>

### Amide group
Two relevant constitutive corrections &lambda;<sub>i</sub> are available, one corresponding to RCONH2 and the second to the Ar-CONH2 group. However, molecules containing an amide group in which the nitrogen is bonded to one or two aliphatic or aryl groups are far more common. Taking this into account, we assumed that the constitutive correction for RCONH2 also applies to RCONHR'R'' fragment, where R' and R'' are aliphatic or aryl groups. The same assumption was made for Ar-CONH2 constitutive correction.

A similar dilemma to that of the acid anhydride was presented by the imide R-C(=O)-NH-C(=O)-R' fragment. Due to a lack of associated &lambda;<sub>i</sub> constant for this group, we assumed the use of two amide-group constitutive corrections.

<p align="center">
<img src="https://github.com/user-attachments/assets/b2d7c6fc-0e76-48e2-b068-d1a90f585920"  alt="Image" width="200">
</p>
<p align="center">
<b>Figure A.3</b> Two &lambda;<sub>i</sub> constants corresponding to the amide group are used to account for imide R-C(=O)-NH-C(=O)-R' fragment.
</p>

### Bicyclic fragments

<p align="center">
<img src="https://github.com/user-attachments/assets/cd1f52bc-f3d4-4460-a90e-2a402b80b957" alt="Image" width="250" >
</p>
<p align="center">
<b>Figure A.4</b> Bicyclo[2.2.1]heptane structure with an atom-numbering scheme. 
</p>

In general, three fused rings can be identified within a bicyclic structure. By examining Figure A.4 of the bicyclo[2.2.1]heptane structure, we can identify three rings with the following atomic indices: 1<sup>st</sup> cyclopentane ring (C1,C2,C3,C4,C7), 2<sup>nd</sup> cyclopentane ring (C1,C6,C5,C4,C7) and the cyclohexane ring (C1,C2,C3,C4,C5,C6). Because these rings share at least two C-C bonds, the application of three constitutive corrections accounting for all three rings would lead to an overestimation of the diamagnetic contribution of a molecule. (In this particular case, this is not relevant as &lambda;<sub>i</sub> of cyclopentane ring equals $0.0 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}$). To address this issue, we introduced *ring seniority* rules, according to which only the constitutive correction of one of the rings is considered. The seniority of the rings was defined based on the ring's &lambda;<sub>i</sub> value, as shown in Figure A.5.

<p align="center">
<img src="https://github.com/user-attachments/assets/5c8bda57-6180-4d2d-8ada-78b76bceaa40" alt="Image" width="550">
</p>
<b>Figure A.5</b> Ring seniority within bicyclic structure. The two dummy rings have no associated  &lambda;<sub>i</sub> values and were introduced solely for code implementation purposes.

### X-CR2-CR2-X bond type (X = Cl or Br)

For the Cl-CR2-CR2-Cl and Br-CR2-CR2-Br fragments, constitutive corrections &lambda;<sub>Cl-CR2-CR2-Cl</sub> and &lambda;<sub>Br-CR2-CR2-Br</sub> are available [ref]. However, applying these constants was forbidden in the case when Cl-CR2-CR2-Cl or Br-CR2-CR2-Br shared three C-C bonds with a ring. To avoid the problem with overlapping bond types, in this particular case, two &lambda;<sub>C-Cl</sub> or &lambda;<sub>C-Br</sub> constants are used, together with given ring's &lambda;<sub>i</sub> value, instead of a single &lambda;<sub>Cl-CR2-CR2-Cl</sub> or &lambda;<sub>Br-CR2-CR2-Br</sub> constant along with ring's &lambda;<sub>i</sub>.


### Amines

Only the constitutive correction of the Ar-NR2 fragment is available. We assumed that this constant can also be applied to the following structurally similar bond types: Ar-NH2, Ar-NHR, Ar-NH-Ar and Ar-N-Ar2. For each of these bond types &lambda;<sub>Ar-NR2</sub> value is applied once.
