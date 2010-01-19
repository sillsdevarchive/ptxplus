<map version="0.9.0">
<!-- To view this file, download free mind mapping software FreeMind from http://freemind.sourceforge.net -->
<node CREATED="1260856737309" ID="ID_1211333900" MODIFIED="1260856745202" TEXT="Typesetting Model">
<node CREATED="1260856746771" ID="ID_1613224022" MODIFIED="1263883560584" POSITION="right" TEXT="Matter Book">
<node CREATED="1260856757431" ID="ID_1984597112" MODIFIED="1260860382687" TEXT="Matter Scripture">
<node CREATED="1260856761503" ID="ID_948167067" MODIFIED="1260856762819" TEXT="Data">
<node CREATED="1260857811584" ID="ID_8308294" MODIFIED="1260857832537" TEXT="id">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  Identifier by which configuration information can be retrieved for this component.
	</p>
  </body>
</html></richcontent>
</node>
<node CREATED="1260856769088" ID="ID_593683797" MODIFIED="1260858459951" TEXT="file">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  This is the text file that will be passed to typesetting engine to produce the PDF output
	</p>
  </body>
</html></richcontent>
</node>
<node CREATED="1260856806648" ID="ID_156065019" MODIFIED="1260856818794" TEXT="source">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  This is the file given by the translator
	</p>
  </body>
</html></richcontent>
</node>
<node CREATED="1260857435686" ID="ID_1842096903" MODIFIED="1260857450842" TEXT="pdf">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  This holds the generated pdf
	</p>
  </body>
</html></richcontent>
</node>
</node>
<node CREATED="1260856763205" ID="ID_707296634" MODIFIED="1260856765939" TEXT="States">
<node CREATED="1260856820799" ID="ID_171185018" MODIFIED="1260856826699" TEXT="Exists">
<node CREATED="1260859965608" ID="ID_1097968666" MODIFIED="1260859966915" TEXT="None">
<node CREATED="1260856846408" ID="ID_1747963751" MODIFIED="1260856869019" TEXT="Create USFM file component"/>
</node>
</node>
<node CREATED="1260857562239" ID="ID_1373853978" MODIFIED="1260857563891" TEXT="Copied">
<node CREATED="1260857570152" ID="ID_246074831" MODIFIED="1260857575827" TEXT="self in exists"/>
<node CREATED="1260859817727" ID="ID_356714434" MODIFIED="1260860147592" TEXT="file newer than source">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  This doesn't happen if the text is locked.
	</p>
  </body>
</html></richcontent>
<node CREATED="1260857622776" ID="ID_265119649" MODIFIED="1260857627811" TEXT="Copy source to file"/>
</node>
</node>
<node CREATED="1260857546008" ID="ID_68283507" MODIFIED="1260857548899" TEXT="Checked">
<node CREATED="1260857554552" ID="ID_1732309636" MODIFIED="1260857559795" TEXT="self in copied">
<node CREATED="1260857639295" ID="ID_1345962601" MODIFIED="1260857669136" TEXT="Run checks"/>
</node>
</node>
<node CREATED="1260857527128" ID="ID_875741449" MODIFIED="1260857530787" TEXT="Typeset">
<node CREATED="1260857536016" ID="ID_504720808" MODIFIED="1260857543657" TEXT="self in checked"/>
<node CREATED="1260859902399" ID="ID_1324568591" MODIFIED="1260859906643" TEXT="pdf newer than file">
<node CREATED="1260859907968" ID="ID_701622663" MODIFIED="1260859911995" TEXT="typeset USFM file"/>
</node>
</node>
</node>
<node CREATED="1260860183431" ID="ID_110603099" MODIFIED="1260860185459" TEXT="Actions">
<node CREATED="1260860186600" ID="ID_1155216579" MODIFIED="1260860188707" TEXT="Lock">
<node CREATED="1260860243056" ID="ID_291175775" MODIFIED="1260860261003" TEXT="self in copied"/>
</node>
</node>
</node>
<node CREATED="1260857057088" ID="ID_1689723550" MODIFIED="1260860383714" TEXT="Book">
<node CREATED="1260857063416" ID="ID_474266836" MODIFIED="1260857065226" TEXT="Data">
<node CREATED="1260857067744" ID="ID_1397054856" MODIFIED="1260860278843" TEXT="children">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  The binding list, an ordered list of components that when combined will create the book
	</p>
  </body>
</html></richcontent>
</node>
</node>
<node CREATED="1260857116056" ID="ID_1661591005" MODIFIED="1260857119042" TEXT="States">
<node CREATED="1260857120213" ID="ID_733435260" MODIFIED="1260857121771" TEXT="Exists">
<node CREATED="1260859953128" ID="ID_803366374" MODIFIED="1260859954763" TEXT="None">
<node CREATED="1260857148184" ID="ID_1648730815" MODIFIED="1260857151722" TEXT="Create Book component"/>
</node>
</node>
<node CREATED="1260857272055" ID="ID_1128672749" MODIFIED="1260857275738" TEXT="Typeset">
<node CREATED="1260857284439" ID="ID_1438517993" MODIFIED="1260860304810" TEXT="children in typeset">
<node CREATED="1260857317600" ID="ID_226437124" MODIFIED="1260857322179" TEXT="Bind components"/>
</node>
</node>
</node>
</node>
<node CREATED="1260857455650" ID="ID_299195129" MODIFIED="1260860385234" TEXT="Matter Peripheral">
<node CREATED="1260857474759" ID="ID_1320776642" MODIFIED="1260858013914" TEXT="Data">
<node CREATED="1260858034159" ID="ID_356201255" MODIFIED="1263883773254" TEXT="id">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  Identifier by which configuration information can be retrieved for this component.
	</p>
  </body>
</html>
</richcontent>
</node>
<node CREATED="1263883773237" ID="ID_1770784374" MODIFIED="1263883846529" TEXT="type">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  Type of peripheral matter this group is
	</p>
  </body>
</html>
</richcontent>
</node>
<node CREATED="1260857477768" ID="ID_790354040" MODIFIED="1263883768025" TEXT="file-working">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  This is the text file that will be passed to typesetting engine to produce the PDF output
	</p>
  </body>
</html>
</richcontent>
</node>
<node CREATED="1260858312134" ID="ID_819415847" MODIFIED="1263883847841" TEXT="file-source">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  This is the source text file given by the translator
	</p>
  </body>
</html>
</richcontent>
</node>
<node CREATED="1260857482351" ID="ID_1886295075" MODIFIED="1263883846849" TEXT="file-pdf">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  This holds the generated pdf
	</p>
  </body>
</html>
</richcontent>
</node>
</node>
<node CREATED="1260858672521" ID="ID_1171257173" MODIFIED="1260858687243" TEXT="States">
<node CREATED="1260858715240" ID="ID_375638973" MODIFIED="1260858724247" TEXT="Exists">
<node CREATED="1260858766826" ID="ID_1660063533" MODIFIED="1260860050563" TEXT="None"/>
</node>
<node CREATED="1260858790896" ID="ID_313542127" MODIFIED="1260858796259" TEXT="Typeset"/>
</node>
</node>
<node CREATED="1260858537960" ID="ID_1232083587" MODIFIED="1263883482325" TEXT="Matter Maps">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  Group of individual map files that are ready for publishing
	</p>
  </body>
</html>
</richcontent>
<node CREATED="1263883346465" ID="ID_1911879395" MODIFIED="1263883899407" TEXT="Map">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  Single rendered map, ready for publishing
	</p>
  </body>
</html>
</richcontent>
<node CREATED="1260858875504" ID="ID_900130548" MODIFIED="1260858880784" TEXT="Data">
<node CREATED="1260858893183" ID="ID_890366276" MODIFIED="1260858896026" TEXT="id"/>
<node CREATED="1263882877991" ID="ID_1249815699" MODIFIED="1263882918480" TEXT="file-style">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  Formating style information for the rendered output
	</p>
  </body>
</html></richcontent>
</node>
<node CREATED="1260858897071" ID="ID_1770752302" MODIFIED="1263883080332" TEXT="file-working">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  Copy of the SVG template that is modifed to create the final output
	</p>
  </body>
</html></richcontent>
</node>
<node CREATED="1260858912855" ID="ID_813327043" MODIFIED="1263882990687" TEXT="file-template">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  Common SVG&#160;template used to combine with data to produce output
	</p>
  </body>
</html></richcontent>
</node>
<node CREATED="1260859080711" ID="ID_1553379298" MODIFIED="1263883158636" TEXT="file-pdf">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  Final output used in final publication
	</p>
  </body>
</html></richcontent>
</node>
<node CREATED="1260858922215" ID="ID_330527835" MODIFIED="1260859231217" TEXT="file-data">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  Data that is used to combine with other elements to make complete output
	</p>
  </body>
</html></richcontent>
</node>
</node>
<node CREATED="1260858882272" ID="ID_1953267984" MODIFIED="1260858885281" TEXT="States"/>
</node>
</node>
<node CREATED="1260859475912" ID="ID_418106951" MODIFIED="1260860387991" TEXT="Matter Grouping">
<node CREATED="1260859497151" ID="ID_1662926898" MODIFIED="1260859530187" TEXT="Data">
<node CREATED="1260859543831" ID="ID_1968731492" MODIFIED="1260859547504" TEXT="Components"/>
</node>
<node CREATED="1260859530824" ID="ID_994991796" MODIFIED="1260859537179" TEXT="States">
<node CREATED="1260859602991" ID="ID_1119180203" MODIFIED="1260859606835" TEXT="Exists">
<node CREATED="1260860022920" ID="ID_313131278" MODIFIED="1260860025211" TEXT="None">
<node CREATED="1260859668816" ID="ID_403810935" MODIFIED="1260859680907" TEXT="Bind components"/>
</node>
</node>
<node CREATED="1260859608888" ID="ID_446438199" MODIFIED="1260859613282" TEXT="Typeset"/>
</node>
</node>
</node>
<node CREATED="1260856752301" ID="ID_355060396" MODIFIED="1260856755106" POSITION="left" TEXT="Action Types">
<node CREATED="1260856874161" ID="ID_1821596932" MODIFIED="1260857380521" TEXT="Create USFM file component">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  Fill in file and source data elements in input component
	</p>
  </body>
</html></richcontent>
</node>
<node CREATED="1260857154912" ID="ID_1059382650" MODIFIED="1260860298117" TEXT="Create Book component">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  Create components for each book in configuration and add in order to children data element. And fill in id for each component.
	</p>
  </body>
</html></richcontent>
</node>
<node CREATED="1260857325560" ID="ID_1418853658" MODIFIED="1260857434719" TEXT="Bind Components">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  Combine pdf files from each of components using pdftk
	</p>
  </body>
</html></richcontent>
</node>
<node CREATED="1260860200110" ID="ID_1852079649" MODIFIED="1260860214711" TEXT="Lock">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  Lock component and all children
	</p>
  </body>
</html></richcontent>
</node>
</node>
<node CREATED="1260856937423" ID="ID_1822903361" MODIFIED="1260856939195" POSITION="left" TEXT="States">
<node CREATED="1260856940567" ID="ID_240108816" MODIFIED="1260856974003" TEXT="Exists">
<richcontent TYPE="NOTE"><html>
  <head>

  </head>
  <body>
	<p>
	  In this state a component exists and is configured ready to do initial processing
	</p>
  </body>
</html></richcontent>
</node>
<node CREATED="1260857297695" ID="ID_925766863" MODIFIED="1260857298755" TEXT="Typeset"/>
</node>
</node>
</map>
