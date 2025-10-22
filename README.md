## 1 Document Goals <a id="document-goals"></a>
 - This document provides a basic introduction to molecular magnetism, outlining the physical quantities and their units, types of magnetic measurements, and computational procedures relevant to the use of the software.
 - Chapter 2 presents the theoretical foundations of the topic. Chapter 3 demonstrates step-by-step calculations of the diamagnetic contribution using several example of chemical compounds. Chapter 4 focuses on the processing and analysis of DC and AC magnetic data.

<!-- ## Document Structure -->
<!-- Not sure if this section is really necessary. From my perspective it introduces noise. We still can have this information, in each section instead. I would rather keep the header simple and stick to Document Goals -->
 <!-- - The section is divided into several chapters. The first chapter briefly explains the concept of diamagnetic susceptibility. The subsequent chapters discuss several examples of chemical compounds for which the diamagnetic contribution has been calculated. To illustrate these computations, we will start with the simplest example and gradually increase the level of difficulty in the following chapters. -->

## Table of Contents
1. [Document Goals](#document-goals)
2. [Introduction](#introduction) 
3. [Diamagnetic contribution](#diamagnetic-contribution)
    1. [Example I](#example-i)
    1. [Example II](#example-ii)
    1. [Example III](#example-iii)
    1. [Example IV](#example-iv)
4. [Processing of magnetic data](#processing-of-magnetic-data)
    1. [DC magnetic data](#dc-magnetic-data)
6. [Literature references](#literature-references)


## 2 Introduction <a id="introduction"></a>

When a sample containing 1 mol of a molecular species is placed in a homogeneous magnetic field *H*, it exhibits a `molar magnetisation` *M*<sub>mol</sub> that is related to *H* by:

$$
\frac{\partial {M_{mol}}}{\partial H} = \chi_{\mathrm{mol}}
$$

<p align="right">
 <span id="eq1"> (1)</span>
</p>


The `molar magnetic susceptibility` &chi;<sub>mol</sub> is a quantitative measure of a sample’s response to an applied magnetic field [<a href="#ref1">1</a>]. In the limit of a weak external magnetic field, &chi;<sub>mol</sub> becomes independent of *H*, leading to the relation:

$$
{M_{mol}} = \chi_{\mathrm{mol}} H
$$

<p align="right">
 <span id="eq2"> (2)</span>
</p>

Materials that are repelled by an applied magnetic field are called diamagnetic, whereas those that are attracted by the field are called paramagnetic. For diamagnets  &chi;<sub>mol</sub> < 0, while for paramagnets  &chi;<sub>mol</sub> > 0. *When material becomes diamagnetic and when paramagnetic?* It depends on its electronic structure. Diamagnetism arises from the interaction of paired [↑↓] electrons with an external magnetic field [<a href="#ref1">2</a>]. Therefore, it is a fundamental property inherent to all matter! In addition to paired electrons, some chemical compounds contain unpaired &nbsp; [↑ ] electrons, which are the source of paramagnetism. The molar magnetic susceptibility is a sum of diamagnetic and paramagnetic susceptibilities:

$$
{\chi_{mol}} = \chi_P + \chi_D
$$

<p align="right">
 <span id="eq3"> (3)</span>
</p>

When the contribution of `diamagnetic susceptibility` &chi;<sub>D</sub> is larger than `paramagnetic susceptibility` &chi;<sub>P</sub>, the material is diamagnetic - it is repelled by the magnetic field. In the opposite scenario (&chi;<sub>P</sub> > &chi;<sub>D</sub>) the material is paramagnetic and it is attracted by the field. Diamagnetic susceptibility is independent of temperature *T* and strength of the applied magnetic field *H*. In contrast, paramagnetic susceptibility depends on temperature and may also vary with the applied magnetic field. These dependencies are rather complex, and become even more complicated when within the material magnetic centers are able to interact with each other, giving rise to phenomena such as ferromagnetism and antiferromagnetism. 

In investigating the magnetic properties of a compound, the focus is placed on its paramagnetic susceptibility. It is extracted by correcting the molar magnetic susceptibility by the diamagnetic contribution.

$$
\chi_P = {\chi_{mol}} - \chi_D
$$

<p align="right">
 <span id="eq4"> (4)</span>
</p>

The diamagnetic susceptibility is mostly an additive quantity. The diamagnetic contribution for given compound may therefore be estimated by summing atomic susceptibilities (&chi;<sub>Di</sub>) and constitutive corrections (&lambda;<sub>i</sub>). The latter takes into account the fact that compounds with multiple bonds exhibit weaker diamagnetic susceptibility than saturated compounds with only single bonds.

$$
\chi_D = \sum_i \chi_{Di} + \sum_i \lambda_i \quad
$$

<p align="right">
 <span id="eq5"> (5)</span>
</p>

&chi;<sub>Di</sub> and &lambda;<sub>i</sub> are so called `Pascal's constants`. These can be found in many scientific books and articles. It should be noted that considerable confusion exists regarding Pascal’s constants, arising from the conflicting values reported in different sources. The article by G. A. Bain *et al.* offers a valuable clarification of this issue, and our software is based on their work [<a href="#ref1">3</a>].

In the reference [<a href="#ref1">3</a>], another method for calculating the diamagnetic contribution is presented. This involves summing the diamagnetic contributions of all species present in the compound. "Species" here refers to, e.g., counterions, ligands and solvent molecules (*vide infra*). The values for common species are tabulated in the article.

$$
\chi_D = \sum_i \chi_{D(species,i)}
$$

<p align="right">
 <span id="eq6"> (6)</span>
</p>

> In the following chapters we will show the procedure for calculating diamagnetic contribution for three examples of chemical compounds.

It is important to note that, for most paramagnetic substances, χ<sub>P</sub> ≫ χ<sub>D</sub>. The χ<sub>D</sub> contribution is small for molecules with low molecular weights. However, this is not always the case. For example, in metalloproteins with molar masses of around 60 000 g/mol, the diamagnetic contribution becomes significant and must be determined with high precision using different methods to obtain an accurate paramagnetic susceptibility [<a href="#ref1">1</a>]. Consequently, the simple addition of Pascal’s constants is no longer valid in such cases. *We note here that the procedure implemented in our software should be used with caution.*


---
> [!NOTE]
> The issue of units in molecular magnetism can often lead to confusion and should be clarified before performing any calculations. First of all, magnetic data are ordinarily expressed in the `cgs-emu` system of units rather than in the standard SI units [<a href="#ref1">1</a>], [<a href="#ref1">2</a>]. For magnetic field strength *H* the SI unit is amper per meter (A/m), while for magnetic induction *B* the SI unit is tesla (T), expressed with SI base units as:
> 
> $$
> \mathrm{T = \frac{kg}{A \cdot s^{2}}}
> $$
> 
> Another useful unit of magnetic induction is gauss (G), which corresponds to 1 G = 10<sup>-4</sup> T. It is important to note that magnetic field strength *H* and magnetic induction *B* are two different physical quantities. In the vacuum these quantities are related by the expression:
>
> $$
> B = \mu_0 H
>$$
> 
> where &mu;<sub>0</sub> is vacuum permeability, in SI units equal to 1.25663706127(20)×10<sup>−6</sup> N⋅A<sup>−2</sup> [<a href="#ref1">4</a>]. In the cgs-emu system unit, however, it is a dimensionless quantity equal to &mu;<sub>0</sub> = 1. For this reason, the magnetic field strength in molecular magnetism is often expressed in gauss. The formal unit of magnetic field strength in the cgs–emu system is the oersted (Oe), corresponding to 1&nbsp;Oe = 1000/4π&nbsp;A m<sup>-1</sup>.
>
> To summarize, in the cgs–emu system, the conversion between the magnetic field units tesla (T), gauss (G), and oersted (Oe) is given by:
>
> $$
> 1 \mathrm{T} = 10^4 \mathrm{Oe} \equiv 10^4 \mathrm{G}
> $$
>
> Following the cgs–emu convention, the unit of molar magnetic susceptibility &chi;<sub>mol</sub> is cm<sup>3</sup> mol<sup>-1</sup> (often written as emu mol<sup>-1</sup>, where dimension of emu is equivalent to cm<sup>3</sup> in this context). Of course, the diamagnetic and paramagnetic susceptibilities, χ<sub>D</sub> and χ<sub>P</sub>, are expressed in the same units. 
> 
> `⚠️ The term emu (electromagnetic unit) is often the source of major confusion in the cgs–emu system. It is not a physical unit itself, but merely an indicator that a quantity is being expressed in electromagnetic cgs units. Depending on context, emu may correspond to the real physical unit erg·G⁻¹ (for magnetic moment) or as an equivalence of cm³ (for magnetic susceptibility). See Chapter 4 for a detailed discussion.`
>
> From [Eq. (2)](#eq2) we can derive the unit of molar magnetization *M*, which is cm<sup>3</sup> G mol<sup>-1</sup>. Another common way to express *M* in the scientific literature is in terms of the *N&mu;*<sub>B</sub> unit, which basically is a multipication of two physical constants, Bohr magneton (*&mu;*<sub>B</sub>) and Avogadro number (*N*) [<a href="#ref1">4</a>]:
>
> $$
> 1 N \mu_B = 6.02214076 \times 10^{23} \ \mathrm{mol^{−1}} \times 9.2740100783(28) \times 10^{−21} \ \mathrm{erg \ G^{−1}} = 5585 \mathrm{erg \ G^{−1} \ mol^{-1}}
> $$
>
> The "erg" is a cgs-emu unit of energy [<a href="#ref1">4</a>]. Because the conversion 1 emu = 1 erg G<sup>-1</sup> = 1 G cm<sup>3</sup> is valid, we can write:
>
> $$
> 1 N \mu_B = 5585 \mathrm{erg \ G^{−1} \ mol^{-1}} = 5585 \ \mathrm{cm^3 \ G \ mol^{-1}}
> $$

&nbsp;

## 3 Diamagnetic contribution <a id="diamagnetic-contribution"></a>
### 3.1 **Example I** - `2-methylpropan-1-ol` <a id="example-i"></a>
> Our first example of a compound for which we will determine the diamagnetic contribution is `2-methylpropan-1-ol`, an alcohol. To calculate the diamagnetic contribution, we use [Eq. (5)](#eq5). 

&nbsp;
<p align="center">
  <img src="https://github.com/user-attachments/assets/9783a0bc-fcfb-4c53-abe4-fe5b18ec0690" width="500" alt="Comound1">
</p>
<p align="center">
  <b>Figure 1</b> Structure of 2-methylpropan-1-ol.
</p>
&nbsp;

Figure 1 shows that 2-methylpropan-1-ol is a neutral molecule in which all atoms are covalently bonded into a branched chain structure. Therefore, expansion of the first sum in the equation is:

$$
\sum_i \chi_{Di} = 4 \chi_{D(C)} + 10 \chi_{D(H)} + \chi_{D(O)}
$$

Taking Pascal's constants from Table 1 from the reference [<a href="#ref1">3</a>], we have:

$$
\sum_i \chi_{Di} = [4 \times (-6.00) + 10 \times (-2.93) + (-4.6)] \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}} = -57.9 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}
$$

Accordingly to Table 2 in [<a href="#ref1">3</a>], C–H and C–C single bonds are set to have a value of constitutive correction $\lambda_i$ equal 0.0 cm<sup>3</sup> mol<sup>-1</sup>. Since there is no information regarding O–H and C–O bonds, they were also assumed to have $\lambda_i$ equal to 0.0 cm<sup>3</sup> mol<sup>-1</sup>. As a result, the sum $\sum_i \lambda_i = 0$ and $\chi_D = \sum_i \chi_{Di} = -57.9 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}$.


&nbsp;
### 3.2 **Example II** - `Chlorobenzene` <a id="example-ii"></a>
> The structure of chlorobenzene consists of a six-membered, benzene ring with alternating single C-C and double C=C bonds (Figure 2). Five carbon atoms are additionally bound to one hydrogen atom, while the last one is connected to a chlorine atom.

&nbsp;
<p align="center">
  <img src="https://github.com/user-attachments/assets/961a1fb6-eedc-483f-a02e-e91c4735dbd0" alt="comound2" width="500">
</p>

<p align="center">
  <b>Figure 2</b> Structure of chlorobenzene.
</p>
&nbsp;

To calculate $\sum_i \chi_{Di}$ sum from [Eq. (5)](#eq5), we need to consider Pascal's constant for carbon atoms within the ring fragment of the molecule, which is $\chi_{C(ring)} = -6.24 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}$ (value taken from Table 1 in [<a href="#ref1">3</a>]). The sum is equal to:

$$
\sum_i \chi_{Di} = 6 \chi_{D(C(ring))} + 5 \chi_{D(H)} + \chi_{D(Cl)} = [6 \times (-6.24) + 5 \times (-2.93) + (-20.1)] \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}} = -72.19 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}
$$

For chlorobenzene, the sum $\sum_i \lambda_i$ in [Eq. (5)](#eq5) is not equal to zero. There are two Pascal's constants that we have to consider: $\lambda_{benzene}$ and $\lambda_{Ar-Cl}$. The first takes into account the presence of the benzene ring within the structure. The second Pascal's constant considers the Ar-Cl bond. Here, "Ar" corresponds to any aromatic fragment (in this particular case benzene fragment). It means that Ar-Cl is a specific case of the C-Cl bond, where the carbon atom corresponds to the aromatic fragment. The resulting sum is:

$$
\sum_i \lambda_i = \lambda_{benzene} + \lambda_{Ar-Cl} = [(–1.4) + (–2.5)] \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}} = -3.9 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}
$$

Finally, the diamagnetic contribution for the compound is:

$$
\chi_D = \sum_i \chi_{Di} + \sum_i \lambda_i  = [(-72.19) + (-3.9)] \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}} = -76.09 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}
$$

### 3.3 **Example III** - `Chalconatronite` <a id="example-iii"></a>
> Chalconatronite is a carbonate mineral with the chemical formula Na<sub>2</sub>Cu(CO<sub>3</sub>)<sub>2</sub>•3H<sub>2</sub>O. This is an ionic compound, which means that some of the atoms are not covalently bonded. Have a look at the structural formula of the mineral (Figure 3):

&nbsp;
<p align="center">
  <img src="https://github.com/user-attachments/assets/217259a8-a64f-4132-9d08-12af35ba8eea" alt="mineral" width="300">
</p>

<p align="center">
  <b>Figure 3</b> Structural formula of chalconatronite.
</p>
&nbsp;

The mineral is composed of two types of cations (species with a positive charge), Cu<sup>2+</sup> and Na<sup>+</sup>, and one type of anion, the carbonate CO<sub>3</sub><sup>2−</sup>. Due to their opposite charges, cations and anions attract each other and are organized into a three-dimensional crystal lattice. Within this lattice, there are additional water molecules. To calculate the $\chi_D$ for chalconatronite, we have to account for the diamagnetic contribution of all species present in the chemical formula of the compound, i.e. we use [Eq. (6)](#eq6) :

$$
\chi_D = 2\chi_{D(Na^+)} + \chi_{D(Cu^{2+})} + 2\chi_{D(CO_3^{2-})} + 3\chi_{D(H_2O)}
$$

Since Na<sup>+</sup> and Cu<sup>2+</sup> are ions, we should use Pascal's constants from Table 6 in [<a href="#ref1">3</a>]. Those are $\chi_{D(Na^+)} = -6.8 \times 10^{-6} \ cm^3 \ mol^{-1}$ and $\chi_{D(Cu^{2+})} = -11 \times 10^{-6} \ cm^3 \ mol^{-1}$, respecetively. We preceed to the carbonate anion, which is a polyatomic charged species. Fortunately, Pascal's constants for common anions were catalogued in Table 3 in [<a href="#ref1">3</a>]. The respective constant equals $\chi_{D(CO_3^{2-})} = -28.0 \times 10^{-6} \ cm^3 \ mol^{-1}$. Our last species is water. The H<sub>2</sub>O molecule is a common ligand (species that can bind to a metal ion), and its Pascal constant, which is listed in Table 4 in [<a href="#ref1">3</a>], is equal to $\chi_{D(H_2O)} = -13 \times 10^{-6} \ cm^3 \ mol^{-1}$. Finally, we have all data to calculate diamagnetic contribution for the mineral:

$$
\chi_D = [2 \times (-6.8) + (-11) + 2 \times (-28.0) + 3 \times (-13)] \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}} = -119.6 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}
$$


### 3.4 **Example IV** - `Coordination compound` <a id="example-iv"></a>
> The coordination compound under consideration has the chemical formula of [Fe<sup>III</sup>(bipy)(phen)(py)(CH<sub>3</sub>OH)]\(PhAs<sup>V</sup>O<sub>3</sub>\)(ClO<sub>4</sub>) and its structural formula is presentend in Figure 4. The compound is composed of complex cation in which the central Fe<sup>3+</sup> binds four different organic molecules (ligands). These molecules are: methanol (CH<sub>3</sub>OH), pyridine (py), 1,10-phenanthroline (phen) and 2,2'-bipirydine (bipy). Since these molecules are neutral, the overall charge of the complex cation is the same as in Fe<sup>3+</sup>. To compensate this positive charge (+3), there are two different anions, phenylarsenate(V) (PhAs<sup>V</sup>O<sub>3</sub><sup>2-</sup>) and perchlorate (ClO<sub>4</sub><sup>-</sup>), having charge of -2 and -1, respectively.

&nbsp;
<p align="center">
 <img src="https://github.com/user-attachments/assets/19212caf-b4bf-415b-a46b-a71eb135c473" alt="most complicated molecule" width="500">
</p>

<p align="center">
  <b>Figure 4</b> Structural formula of complex [Fe<sup>III</sup>(bipy)(phen)(py)(CH<sub>3</sub>OH)](PhAs<sup>V</sup>O<sub>3</sub>)(ClO<sub>4</sub>).
</p>

&nbsp;

The overall diamagnetic susceptibility of our coordination compound is equal to the sum of the diamagnetic contributions from the complex cation [Fe<sup>III</sup>(bipy)(phen)(py)(CH<sub>3</sub>OH)]<sup>3+</sup> and the two anions PhAs<sup>V</sup>O<sub>3</sub><sup>2-</sup> and ClO<sub>4</sub><sup>-</sup>, as follows:

$$
\chi_D = \chi_{D\([ \mathrm{Fe^{III}(bipy)(phen)(py)(CH_3OH)]^{3+}} \)} + \chi_{D(\mathrm{PhAs^{V}O_3^{2-}}\)} + \chi_{D(\mathrm{ClO_4^{-}}\)}
$$

Although the structure of the complex cation looks scary, calculating the diamagnetic contribution for this species is fairly straightforward. This is because Table 4 in [<a href="#ref1">3</a>] provides Pascal's constants for all the ligands present in the complex cation [Fe<sup>III</sup>(bipy)(phen)(py)(CH<sub>3</sub>OH)]<sup>3+</sup> except mehtanol. The Pascal's constant for methanol is found in Table 5 [<a href="#ref1">3</a>]. The only remaining value is the Pascal's constant for the Fe<sup>3+</sup> cation, which we take from Table 6 [<a href="#ref1">3</a>]. Based on given data, we have:

$$
\chi_{D\([ \mathrm{Fe^{III}(bipy)(phen)(py)(CH_3OH)]^{3+}} \)} = \chi_{D\(Fe^{3+})} + \chi_{D\(bipy)} + \chi_{D\(phen)} + \chi_{D\(py)} + \chi_{D\(CH_3OH)}
$$

$$
\chi_{D\([ \mathrm{Fe^{III}(bipy)(phen)(py)(CH_3OH)]^{3+}} \)} = [(-10) + (-105) + (-128) + (-49) + (-21.4)] \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}} = -313.4 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}
$$

We now proceed to the two anions of our coordination compound. In the case of perchlorate anion, the diamagnetic contribution is given in Table 3 in [<a href="#ref1">3</a>] and is equal to $\chi_{D(ClO_4^{-})} = -32.0 \times 10^{-6} \ cm^3 \ mol^{-1}$. For the second anion, phenylarsenate(V) (PhAs<sup>V</sup>O<sub>3</sub><sup>2-</sup>), the situation is more complicated as magnetic contribution for this species is not listed in Tables 3 and 4 in the reference, so we need to calculate it stepwise. The calculations are similar as for Example II (see chapter 3.2):

$$
\chi_{D(\mathrm{PhAs^{V}O_3^{2-}}\)} = \sum_i \chi_{Di} + \sum_i \lambda_i \quad
$$

We calculate first sum using Pascal's constants of all elements present, remembering to choose appropriate value (Table 1 in [<a href="#ref1">3</a>]). Note that all carbon atoms form ring, while arsenic atom exhibits oxidation state of V. It should also be noted that our procedure does not account for the overall negative charge of the anion, leading to an overestimation of the final value.

$$
\sum_i \chi_{Di} = 6 \chi_{D(C(ring))} + 5 \chi_{D(H)} + \chi_{D(As^{V})} + 3 \chi_{D(O)}
$$

$$
\sum_i \chi_{Di} = [6 \times (-6.24) + 5 \times (-2.93) + (-43.0) + 3 \times (-4.6)] \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}} = -108.89 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}
$$

To calculate the sum $\sum_i \lambda_i$, the only Pascal's constant that we have to account is this related to benzene ring. In fact, the Table 2 in the article does not list any Pascal’s constants corresponding to bonds involving arsenic, so those values were assume to be equal to $0 \ \mathrm{cm^3 \ mol^{-1}}$. We have:

$$
\sum_i \lambda_i \quad = \lambda_{benzene} = -1.4 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}
$$

And the overall diamagnetic contribution for the anion is:

$$
\chi_{D(\mathrm{PhAs^{V}O_3^{2-}}\)} = [(-108.89) + (-1.4)] \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}} = -110.29 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}
$$

Finally, the diamagnetic contribution of our coordination compound can be calculated as follows:

$$
\chi_D = \chi_{D\([ \mathrm{Fe^{III}(bipy)(phen)(py)(CH_3OH)]^{3+}} \)} + \chi_{D(\mathrm{PhAs^{V}O_3^{2-}}\)} + \chi_{D(\mathrm{ClO_4^{-}}\)}
$$

$$
\chi_D = [(-313.4) + (-32.0) + (-110.29)] \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}} = -455.69 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}
$$

&nbsp;

## 4. Processing of magnetic data <a id="processing-of-magnetic-data"></a>

> [!IMPORTANT]
> Molar magnetic susceptibility &chi;<sub>mol</sub> is not a quantity that we directly obtain from magnetic measurements and it must be determined. In general, there are two types of measurements commonly performed to investigate the magnetic properties of a sample [<a href="#ref1">5</a>]:
> 
> 1) **Temperature-dependent magnetization measurement**
>    - The magnetization is acquired over a temperature range, typically 2–300 K. During the measurement, a constant external magnetic field is applied.
>    - The processed data are expressed in the form of &chi;<sub>P</sub> = *f*(T) and &chi;<sub>P</sub>T = *f*(T) plots.
>
> 2) **Field-dependent magnetization measurement**
>    - The magnetization data are collected over a range of magnetic field strengths. The measurements are performed at a constant, very low temperature, typically 2–8 K.
>    - After processing, the data are shown in the form of an *M*<sub>mol</sub> = *f*(H) plot.
>

&nbsp;

These two types of measurements are known as `direct current (DC) magnetic measurements`. In this methods, the magnetometer applies a steady magnetic field, records the sample’s magnetization (M) response, and repeats the procedure under different temperature or field conditions. 

Magnetization measurements can also be performed using an alternating current (AC) magnetic field. In the `AC magnetic measurements`, the applied field oscillates in time, inducing a time-dependent magnetization that provides information about the dynamic magnetic behavior of the material.

&nbsp;
### 4.1 DC magnetic data <a id="dc-magnetic-data"></a>

> ### Temperature-dependent magnetization measurements

The raw data reported by the magnetometer in this case is the `total magnetic moment` (*M*), measured at different temperatures. This total magnetic moment originates from both the sample and the holder in which it is placed. The holder gives rise to an additional background magnetization, *M*<sub>holder</sub>. The `sample’s magnetization` *M*<sub>sample</sub> is obtained by correcting the total moment with the holder contribution: 

$$
M_{\mathrm{sample}} = M - M_{\mathrm{holder}}
$$

> ⚠️ correction must be applied for each temperature data point.

&nbsp;

 *M*<sub>sample</sub> is usually expressed in units of emu = erg/G (see further discussion). For further data processing, the mass of the sample (*m*) is required and should be included in the magnetometer’s report. 
> ⚠️ Note that the sample's mass is usually given in mg and must be converted to g prior to use.

Now we can calculate `mass magnetization` *M*<sub>g</sub>:

$$
M_{\mathrm{g}} = \frac{M_{\mathrm{sample}}}{m}
$$

Some sources [<a href="#ref1">2</a>] introduce `volume magnetization` (*M*<sub>V</sub>) which is obtained by dividing the total magnetic moment of the sample by its volume (V), expressed in cm<sup>3</sup>.

$$
M_{\mathrm{V}} = \frac{M_{\mathrm{sample}}}{V}
$$

Since the density (*&rho;*) of the sample equals *&rho;* = m/V (unit: g cm<sup>-3</sup>), it can be used to convert between volume and mass magnetization:

$$
M_{\mathrm{g}} = \frac{M_{\mathrm{V}}}{\rho}
$$

Next step is to calculate the molar magnetization *M*<sub>mol</sub>. To do this we use the molar mass *M*<sub>mass</sub> of the studied compound (unit: g/mol):

$$
M_{\mathrm{mol}} = M_{\mathrm{g}} \times {M_{\mathrm{mass}}} 
$$

Given that the amount of the sample *n* = <sup>*m*</sup>&frasl;<sub>*M*<sub>mass</sub></sub> (unit for *n* is mol), we also have:


$$
M_{\mathrm{mol}} = \frac{M_{\mathrm{sample}}}{n} 
$$

> [!IMPORTANT]
> Once *M*<sub>mol</sub> is determined, we can use [Eq. (2)](#eq2) to calculate molar magnetic susceptibility *&chi;*<sub>mol</sub>. Then we can calculate the diamagnetic contribution for the studied compound with one of the procedures discussed in Chapter 3. Finally, [Eq. (4)](#eq4) is applied to obtain paramagnetic susceptibility *&chi;*<sub>P</sub>, which is the key quantity for investigating magnetic behavior of the compounds. Specifically, the dependencies &chi;<sub>P</sub> = *f*(T) and &chi;<sub>P</sub>T = *f*(T) are the focus of the analysis.

&nbsp;

Numerous software packages have been developed to calculate the magnetic properties of paramagnetic compounds, such as PHI [<a href="#ref1">6</a>]. In these programs, the experimental &chi;<sub>P</sub> = *f*(T) and &chi;<sub>P</sub>T = *f*(T) dependencies are used as input for subsequent simulations.

&nbsp;
> [!NOTE]
> 
> As we mentioned earlier, the use of cgs-emu units of magnetisation quantities is a common source of confusion [<a href="#ref1">7</a>]. Magnetisation of the sample *M*<sub>sample</sub> is expressed in the units of emu, where 1 emu = 1 erg G<sup>-1</sup>.
>
> **We remind that:**
>  `⚠️ The term emu (electromagnetic unit) is often the source of major confusion in the cgs–emu system. It is not a physical unit itself, but merely an indicator that a quantity is being expressed in electromagnetic cgs units. Depending on context, emu may correspond to the real physical unit erg·G⁻¹ (for magnetic moment) or as an equivalence of cm³ (for magnetic susceptibility).`
> 
> The unit of volume magnetisation *M*<sub>V</sub> is erg G<sup>-1</sup> cm<sup>-3</sup>. It is sometimes incorrectly reported in G. The SI conversion of 1 G is 10<sup>3</sup>/4&pi; A m<sup>−1</sup>, and the quantity that is properly expressed in G is not *M*<sub>V</sub> itself but the volume magnetization multiplied by 4&pi;, i.e., 4&pi;*M*<sub>V</sub>.
>
> When *M*<sub>V</sub> is divided by magnetic field strength *H* (unit: G), the volume magnetic susceptibility *&chi;*<sub>V</sub> is obtained (*M*<sub>V</sub>/*H* = *&chi;*<sub>V</sub>). *&chi;*<sub>V</sub> is a unitless quantity, but some physicists express this quantity with the units of emu cm<sup>-3</sup> [<a href="#ref1">8</a>]. Here, 1 emu is equivalent to cm<sup>-3</sup> which legitimate this conversion, as 1 emu cm<sup>-3</sup> = 1.
>
> Mass magnetisation *M*<sub>g</sub> is expressed in emu g<sup>-1</sup>, and at first glance the same notation seems to apply to the mass magnetic susceptibility (*&chi;*<sub>g</sub>), defined by *M*<sub>g</sub>/*H* = *&chi;*<sub>g</sub>. In reality, the term emu g<sup>-1</sup> has different meanings in the two contexts.
>   - For *M*<sub>g</sub>, 1 emu g<sup>-1</sup> = 1 erg G<sup>-1</sup> g<sup>-1</sup>, 
>   - For *&chi;*<sub>g</sub>, 1 emu/g is equivalent to 1 cm<sup>3</sup> g<sup>-1</sup>.
>
> Similar situation holds for the term emu mol<sup>-1</sup> used to desribe units of the molar magnetisation *M*<sub>mol</sub> and molar susceptibility *&chi;*<sub>mol</sub>.
>   - For *M*<sub>mol</sub>, 1 emu mol<sup>-1</sup> = 1 erg G<sup>-1</sup> mol<sup>-1</sup>. Because the conversion 1 emu = 1 erg G<sup>-1</sup> = 1 G cm<sup>3</sup> is valid, *M*<sub>mol</sub> can also be expressed with the unit of cm<sup>3</sup> G mol<sup>-1</sup>.
>   - For *&chi;*<sub>mol</sub>, 1 emu mol<sup>-1</sup> corresponds to 1 cm<sup>3</sup> mol<sup>-1</sup>.
&nbsp;

> ### Field-dependent magnetization measurements

## 4 Literature references <a id="literature-references"></a>
> <a id="ref1"></a>[1] O. Kahn, *Molecular Magnetism*, VCH, 1993.
>
> <a id="ref1"></a>[2] R. L. Carlin, *Magnetochemistry*, Springer-Verlag, 1986.
> 
>  <a id="ref1"></a>[3] G. A. Bain, J. F. Berry, J. Chem. Educ., 2008, 85, 532-536. DOI: https://doi.org/10.1021/ed085p532
>
>  <a id="ref1"></a>[4] Wikipedia (articles: [vacuum permeability](https://en.wikipedia.org/wiki/Vacuum_permeability), [Bohr magneton](https://en.wikipedia.org/wiki/Bohr_magneton), [cgs-emu unit system](https://en.wikipedia.org/wiki/Centimetre%E2%80%93gram%E2%80%93second_system_of_units#EMU_notation), [Avogadro constant](https://en.wikipedia.org/wiki/Avogadro_constant), [Tesla unit](https://en.wikipedia.org/wiki/Tesla_(unit)), [Gauss unit](https://en.wikipedia.org/wiki/Gauss_(unit)), [erg unit](https://en.wikipedia.org/wiki/Erg))
>
> <a id="ref1"></a>[5] S. Mugiraneza, A. M. Hallas, Commun. Phys., 2022, 5, 95. DOI: https://doi.org/10.1038/s42005-022-00853-y
> 
> <a id="ref1"></a>[6] N. F. Chilton, R. P. Anderson, L. D. Turner, A. Soncini and K. S. Murray, *J. Comput. Chem.*, 2013, 34, 1164-1175. [PHI](https://www.nfchilton.com/phi.html)
>
> <a id="ref1"></a>[7] R. B. Goldfarb, *IEEE Magn Lett.*, 2018, 9, DOI: https://doi.org/10.1109/LMAG.2018.2868654
> 
> <a id="ref1"></a>[8] [magnetisation units](https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://users.ox.ac.uk/~sjb/magnetism/units.pdf&ved=2ahUKEwiBt6DM85qQAxXwBBAIHZoEOE4QFnoECBgQAQ&usg=AOvVaw3Bn4ljFiHMbVIDNGro2GVU)


